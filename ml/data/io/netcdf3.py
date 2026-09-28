"""
Zero-dependency, pure-Python + NumPy NetCDF-3 Classic / 64-bit Offset reader and writer.
Compliant with the NetCDF File Format Specification (CDF-1 and CDF-2).
Enables reading and writing of HURSAT-B1 and other CF-compliant meteorological NetCDF files
without requiring external C-libraries.
"""

import struct
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

# NetCDF-3 Data Types
NC_BYTE = 1
NC_CHAR = 2
NC_SHORT = 3
NC_INT = 4
NC_FLOAT = 5
NC_DOUBLE = 6

_NC_TYPE_MAP = {
    NC_BYTE: (">i1", 1),
    NC_CHAR: ("S1", 1),
    NC_SHORT: (">i2", 2),
    NC_INT: (">i4", 4),
    NC_FLOAT: (">f4", 4),
    NC_DOUBLE: (">f8", 8),
}

_NUMPY_TO_NC = {
    np.dtype("int8"): NC_BYTE,
    np.dtype("uint8"): NC_BYTE,
    np.dtype("int16"): NC_SHORT,
    np.dtype(">i2"): NC_SHORT,
    np.dtype("<i2"): NC_SHORT,
    np.dtype("int32"): NC_INT,
    np.dtype(">i4"): NC_INT,
    np.dtype("<i4"): NC_INT,
    np.dtype("float32"): NC_FLOAT,
    np.dtype(">f4"): NC_FLOAT,
    np.dtype("<f4"): NC_FLOAT,
    np.dtype("float64"): NC_DOUBLE,
    np.dtype(">f8"): NC_DOUBLE,
    np.dtype("<f8"): NC_DOUBLE,
}

TAG_DIMENSION = 0x0000000A
TAG_VARIABLE = 0x0000000B
TAG_ATTRIBUTE = 0x0000000C
TAG_NONE = 0x00000000


def _pad4(size: int) -> int:
    return (size + 3) & ~3


class NetCDF3Variable:
    """Represents a NetCDF-3 variable."""

    def __init__(
        self,
        name: str,
        dimensions: Tuple[str, ...],
        nc_type: int,
        data: Optional[np.ndarray] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.dimensions = dimensions
        self.nc_type = nc_type
        self.attributes = attributes or {}
        self._data = data

    @property
    def data(self) -> np.ndarray:
        if self._data is None:
            raise ValueError(f"Variable '{self.name}' has no loaded data.")
        return self._data

    @data.setter
    def data(self, value: np.ndarray):
        self._data = value

    @property
    def shape(self) -> Tuple[int, ...]:
        return self._data.shape if self._data is not None else ()

    @property
    def dtype(self) -> np.dtype:
        return self._data.dtype if self._data is not None else np.dtype("float32")

    def __getitem__(self, item):
        return self.data[item]


class NetCDF3Dataset:
    """
    Reader and writer for NetCDF-3 classic (CDF-1) and 64-bit offset (CDF-2) files.
    """

    def __init__(self, filename: Optional[str] = None, mode: str = "r"):
        self.filename = filename
        self.mode = mode
        self.dimensions: Dict[str, int] = {}
        self.attributes: Dict[str, Any] = {}
        self.variables: Dict[str, NetCDF3Variable] = {}
        self.numrecs: int = 0
        self.is_64bit: bool = False

        if filename and "r" in mode:
            self._read(filename)

    def _read(self, filename: str):
        with open(filename, "rb") as f:
            raw = f.read()

        magic = raw[:4]
        if magic == b"CDF\x01":
            self.is_64bit = False
        elif magic == b"CDF\x02":
            self.is_64bit = True
        elif magic == b"\x89HDF":
            self._read_netcdf4(filename)
            return
        else:
            raise ValueError(f"Not a valid NetCDF-3 file (Magic: {magic!r})")

        offset = 4
        (self.numrecs,) = struct.unpack(">i", raw[offset : offset + 4])
        offset += 4

        # Read dimensions
        (dim_tag,) = struct.unpack(">i", raw[offset : offset + 4])
        offset += 4
        if dim_tag == TAG_DIMENSION:
            (num_dims,) = struct.unpack(">i", raw[offset : offset + 4])
            offset += 4
            for _ in range(num_dims):
                name, offset = self._read_string(raw, offset)
                (dim_len,) = struct.unpack(">i", raw[offset : offset + 4])
                offset += 4
                self.dimensions[name] = dim_len
        elif dim_tag != TAG_NONE:
            raise ValueError(f"Corrupted dimension tag: {dim_tag:#x}")

        # Read global attributes
        (gatt_tag,) = struct.unpack(">i", raw[offset : offset + 4])
        offset += 4
        if gatt_tag == TAG_ATTRIBUTE:
            (num_gatts,) = struct.unpack(">i", raw[offset : offset + 4])
            offset += 4
            for _ in range(num_gatts):
                name, val, offset = self._read_attribute(raw, offset)
                self.attributes[name] = val
        elif gatt_tag != TAG_NONE:
            raise ValueError(f"Corrupted global attribute tag: {gatt_tag:#x}")

        # Read variables
        (var_tag,) = struct.unpack(">i", raw[offset : offset + 4])
        offset += 4
        var_headers = []
        dim_names = list(self.dimensions.keys())

        if var_tag == TAG_VARIABLE:
            (num_vars,) = struct.unpack(">i", raw[offset : offset + 4])
            offset += 4
            for _ in range(num_vars):
                var_name, offset = self._read_string(raw, offset)
                (num_var_dims,) = struct.unpack(">i", raw[offset : offset + 4])
                offset += 4
                var_dim_ids = struct.unpack(f">{num_var_dims}i", raw[offset : offset + num_var_dims * 4])
                offset += num_var_dims * 4
                var_dims = tuple(dim_names[i] for i in var_dim_ids)

                # Variable attributes
                (vatt_tag,) = struct.unpack(">i", raw[offset : offset + 4])
                offset += 4
                var_atts = {}
                if vatt_tag == TAG_ATTRIBUTE:
                    (num_vatts,) = struct.unpack(">i", raw[offset : offset + 4])
                    offset += 4
                    for _ in range(num_vatts):
                        aname, aval, offset = self._read_attribute(raw, offset)
                        var_atts[aname] = aval

                (var_type, vsize) = struct.unpack(">2i", raw[offset : offset + 8])
                offset += 8

                if self.is_64bit:
                    (vbegin,) = struct.unpack(">q", raw[offset : offset + 8])
                    offset += 8
                else:
                    (vbegin,) = struct.unpack(">i", raw[offset : offset + 4])
                    offset += 4

                var_headers.append((var_name, var_dims, var_type, var_atts, vbegin, vsize))

        # Read variable data arrays
        for var_name, var_dims, var_type, var_atts, vbegin, vsize in var_headers:
            dtype_str, elem_size = _NC_TYPE_MAP[var_type]
            shape = tuple(self.dimensions[d] for d in var_dims)
            total_elements = 1
            for s in shape:
                total_elements *= s

            data_bytes = raw[vbegin : vbegin + total_elements * elem_size]
            if var_type == NC_CHAR:
                arr = np.frombuffer(data_bytes, dtype=np.dtype(dtype_str))
            else:
                arr = np.frombuffer(data_bytes, dtype=np.dtype(dtype_str)).astype(dtype_str.replace(">", "="))

            if shape:
                arr = arr.reshape(shape)

            # Apply scale_factor and add_offset if present
            if "scale_factor" in var_atts or "add_offset" in var_atts:
                scale = float(var_atts.get("scale_factor", 1.0))
                offset_val = float(var_atts.get("add_offset", 0.0))
                float_arr = arr.astype(np.float32)
                if "_FillValue" in var_atts:
                    fill = var_atts["_FillValue"]
                    mask = arr == fill
                    float_arr = float_arr * scale + offset_val
                    float_arr[mask] = np.nan
                else:
                    float_arr = float_arr * scale + offset_val
                var_obj = NetCDF3Variable(var_name, var_dims, var_type, float_arr, var_atts)
            else:
                var_obj = NetCDF3Variable(var_name, var_dims, var_type, arr, var_atts)

            self.variables[var_name] = var_obj

    def _read_string(self, raw: bytes, offset: int) -> Tuple[str, int]:
        (length,) = struct.unpack(">i", raw[offset : offset + 4])
        offset += 4
        s = raw[offset : offset + length].decode("utf-8", errors="replace")
        offset += _pad4(length)
        return s, offset

    def _read_attribute(self, raw: bytes, offset: int) -> Tuple[str, Any, int]:
        name, offset = self._read_string(raw, offset)
        (nc_type, nelems) = struct.unpack(">2i", raw[offset : offset + 8])
        offset += 8
        dtype_str, elem_size = _NC_TYPE_MAP[nc_type]
        byte_len = nelems * elem_size
        val_bytes = raw[offset : offset + byte_len]
        offset += _pad4(byte_len)

        if nc_type == NC_CHAR:
            val = val_bytes.decode("utf-8", errors="replace")
        elif nc_type in (NC_BYTE, NC_SHORT, NC_INT):
            arr = np.frombuffer(val_bytes, dtype=np.dtype(dtype_str))
            val = int(arr[0]) if nelems == 1 else arr.tolist()
        else:
            arr = np.frombuffer(val_bytes, dtype=np.dtype(dtype_str))
            val = float(arr[0]) if nelems == 1 else arr.tolist()

        return name, val, offset

    def create_dimension(self, name: str, length: int):
        self.dimensions[name] = length

    def create_variable(
        self,
        name: str,
        nc_type: int,
        dimensions: Tuple[str, ...],
        attributes: Optional[Dict[str, Any]] = None,
        data: Optional[np.ndarray] = None,
    ) -> NetCDF3Variable:
        var = NetCDF3Variable(name, dimensions, nc_type, data, attributes)
        self.variables[name] = var
        return var

    def write(self, filename: str):
        """Writes current dataset to a NetCDF-3 Classic file."""
        buf = bytearray()
        # Magic: CDF-1
        buf.extend(b"CDF\x01")
        # numrecs
        buf.extend(struct.pack(">i", self.numrecs))

        # Dimensions
        if self.dimensions:
            buf.extend(struct.pack(">2i", TAG_DIMENSION, len(self.dimensions)))
            for dname, dlen in self.dimensions.items():
                name_b = dname.encode("utf-8")
                buf.extend(struct.pack(">i", len(name_b)))
                buf.extend(name_b)
                buf.extend(b"\x00" * (_pad4(len(name_b)) - len(name_b)))
                buf.extend(struct.pack(">i", dlen))
        else:
            buf.extend(struct.pack(">i", TAG_NONE))

        # Global attributes
        if self.attributes:
            buf.extend(struct.pack(">2i", TAG_ATTRIBUTE, len(self.attributes)))
            for aname, aval in self.attributes.items():
                self._write_attribute(buf, aname, aval)
        else:
            buf.extend(struct.pack(">i", TAG_NONE))

        # Variables header
        dim_keys = list(self.dimensions.keys())
        if self.variables:
            buf.extend(struct.pack(">2i", TAG_VARIABLE, len(self.variables)))
            var_offsets = {}
            for vname, var in self.variables.items():
                name_b = vname.encode("utf-8")
                buf.extend(struct.pack(">i", len(name_b)))
                buf.extend(name_b)
                buf.extend(b"\x00" * (_pad4(len(name_b)) - len(name_b)))

                # Dims
                buf.extend(struct.pack(">i", len(var.dimensions)))
                for d in var.dimensions:
                    buf.extend(struct.pack(">i", dim_keys.index(d)))

                # Attributes
                if var.attributes:
                    buf.extend(struct.pack(">2i", TAG_ATTRIBUTE, len(var.attributes)))
                    for aname, aval in var.attributes.items():
                        self._write_attribute(buf, aname, aval)
                else:
                    buf.extend(struct.pack(">i", TAG_NONE))

                # Type and vsize
                dtype_str, elem_size = _NC_TYPE_MAP[var.nc_type]
                total_elems = 1
                for d in var.dimensions:
                    total_elems *= self.dimensions[d]
                vsize = total_elems * elem_size
                buf.extend(struct.pack(">2i", var.nc_type, vsize))

                # Placeholder for vbegin (4 bytes)
                var_offsets[vname] = len(buf)
                buf.extend(b"\x00\x00\x00\x00")
        else:
            buf.extend(struct.pack(">i", TAG_NONE))

        # Align to 4 bytes before data section
        pad_header = _pad4(len(buf)) - len(buf)
        buf.extend(b"\x00" * pad_header)

        # Write variable data
        for vname, var in self.variables.items():
            begin_pos = len(buf)
            # Patch vbegin in header
            offset_slot = var_offsets[vname]
            buf[offset_slot : offset_slot + 4] = struct.pack(">i", begin_pos)

            if var._data is not None:
                dtype_str, elem_size = _NC_TYPE_MAP[var.nc_type]
                raw_bytes = var._data.astype(dtype_str).tobytes()
                buf.extend(raw_bytes)
                pad_data = _pad4(len(raw_bytes)) - len(raw_bytes)
                buf.extend(b"\x00" * pad_data)

        with open(filename, "wb") as f:
            f.write(buf)

    def _write_attribute(self, buf: bytearray, name: str, val: Any):
        name_b = name.encode("utf-8")
        buf.extend(struct.pack(">i", len(name_b)))
        buf.extend(name_b)
        buf.extend(b"\x00" * (_pad4(len(name_b)) - len(name_b)))

        if isinstance(val, str):
            val_b = val.encode("utf-8")
            buf.extend(struct.pack(">2i", NC_CHAR, len(val_b)))
            buf.extend(val_b)
            buf.extend(b"\x00" * (_pad4(len(val_b)) - len(val_b)))
        elif isinstance(val, (int, np.integer)):
            buf.extend(struct.pack(">2i", NC_INT, 1))
            buf.extend(struct.pack(">i", int(val)))
        elif isinstance(val, (float, np.floating)):
            buf.extend(struct.pack(">2i", NC_FLOAT, 1))
            buf.extend(struct.pack(">f", float(val)))
        elif isinstance(val, (list, tuple)):
            if len(val) > 0 and isinstance(val[0], (int, np.integer)):
                buf.extend(struct.pack(">2i", NC_INT, len(val)))
                for v in val:
                    buf.extend(struct.pack(">i", int(v)))
            else:
                buf.extend(struct.pack(">2i", NC_FLOAT, len(val)))
                for v in val:
                    buf.extend(struct.pack(">f", float(v)))
        else:
            s = str(val).encode("utf-8")
            buf.extend(struct.pack(">2i", NC_CHAR, len(s)))
            buf.extend(s)
            buf.extend(b"\x00" * (_pad4(len(s)) - len(s)))

    def _read_netcdf4(self, filename: str):
        """Reads NetCDF-4 / HDF5 file using netCDF4 library."""
        try:
            import netCDF4
        except ImportError:
            raise ImportError("netCDF4 package is required to read NetCDF-4/HDF5 format files.")

        ds = netCDF4.Dataset(filename, "r")
        try:
            self.dimensions = {name: len(dim) for name, dim in ds.dimensions.items()}
            self.attributes = {att: ds.getncattr(att) for att in ds.ncattrs()}
            for var_name, var in ds.variables.items():
                v_atts = {att: var.getncattr(att) for att in var.ncattrs()}
                arr = var[:]
                if hasattr(arr, "filled"):
                    if np.issubdtype(arr.dtype, np.floating):
                        arr = arr.filled(np.nan)
                    elif np.issubdtype(arr.dtype, np.integer):
                        arr = arr.astype(np.float32).filled(np.nan)
                    else:
                        arr = arr.filled()
                if arr.ndim == 3 and arr.shape[0] == 1:
                    arr = arr[0]
                arr_data = arr.astype(np.float32) if (np.issubdtype(arr.dtype, np.floating) or np.issubdtype(arr.dtype, np.integer)) else arr
                self.variables[var_name] = NetCDF3Variable(
                    name=var_name,
                    dimensions=tuple(var.dimensions),
                    nc_type=NC_FLOAT,
                    data=arr_data,
                    attributes=v_atts,
                )
        finally:
            ds.close()

    def close(self):
        """No-op for in-memory NetCDF3Dataset."""
        pass


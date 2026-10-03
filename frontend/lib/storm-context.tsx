"use client";

import React, { createContext, useContext, useState, useCallback, useMemo } from "react";
import {
  CentralStormState,
  CHAPALA_CENTRAL_STORM,
  ALTERNATIVE_STORMS,
  getCentralStormState,
  DEFAULT_OBSERVATION_SOURCES,
  ObservationSourceItem,
  AuthorizedHumanReviewData,
  TargetedAlertItem,
} from "./central-storm-store";

export type FusionSequenceStep = "idle" | "receiving" | "validating" | "aligning" | "fusing" | "complete";
export type AnalysisSequenceStep = "idle" | "extracting" | "segmenting" | "inferring" | "complete";

interface StormContextType {
  currentStorm: CentralStormState;
  selectStorm: (stormId: string) => void;
  availableStorms: Array<{ id: string; name: string; basin: string }>;
  
  // Data Fusion Workflow
  observationSources: ObservationSourceItem[];
  toggleSourceStatus: (sourceId: string) => void;
  setSourceStatus: (sourceId: string, status: ObservationSourceItem["status"]) => void;
  isFusing: boolean;
  fusionSequence: FusionSequenceStep;
  fusionComplete: boolean;
  triggerFusion: () => Promise<void>;
  
  // AI Analysis Workflow
  isAnalyzing: boolean;
  analysisSequence: AnalysisSequenceStep;
  analysisComplete: boolean;
  triggerAnalysis: () => Promise<void>;
  
  // Dynamic Confidence & Explainability
  calculatedConfidence: number;
  confidencePenaltyTotal: number;
  missingSourcesList: ObservationSourceItem[];

  // Alerts & Authority Review
  authorizeAlert: (alertId: string) => void;
  authorizeAllAlerts: () => void;
  updateHumanReview: (notes: string, status?: AuthorizedHumanReviewData["review_status"]) => void;
  isFullyAuthorized: boolean;
  activeTabStage: number;
  setActiveTabStage: (stage: number) => void;
}

const StormContext = createContext<StormContextType | undefined>(undefined);

export function StormProvider({ children }: { children: React.ReactNode }) {
  const [selectedStormId, setSelectedStormId] = useState<string>(CHAPALA_CENTRAL_STORM.storm_id);
  const [stormOverrides, setStormOverrides] = useState<Record<string, Partial<CentralStormState>>>({});
  const [activeTabStage, setActiveTabStage] = useState<number>(1);

  // Observation sources state per storm
  const [sourcesByStorm, setSourcesByStorm] = useState<Record<string, ObservationSourceItem[]>>({
    [CHAPALA_CENTRAL_STORM.storm_id]: [...DEFAULT_OBSERVATION_SOURCES],
  });

  // Fusion & Analysis workflow states
  const [isFusing, setIsFusing] = useState<boolean>(false);
  const [fusionSequence, setFusionSequence] = useState<FusionSequenceStep>("idle");
  const [fusionComplete, setFusionComplete] = useState<boolean>(false);

  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisSequence, setAnalysisSequence] = useState<AnalysisSequenceStep>("idle");
  const [analysisComplete, setAnalysisComplete] = useState<boolean>(false);

  const availableStorms = useMemo(
    () =>
      Object.values(ALTERNATIVE_STORMS).map((s) => ({
        id: s.storm_id,
        name: s.storm_name,
        basin: s.basin_name,
      })),
    []
  );

  const observationSources = useMemo(() => {
    return sourcesByStorm[selectedStormId] || DEFAULT_OBSERVATION_SOURCES;
  }, [sourcesByStorm, selectedStormId]);

  // Missing sources and confidence calculation
  const missingSourcesList = useMemo(() => {
    return observationSources.filter((s) => s.status === "Missing");
  }, [observationSources]);

  const confidencePenaltyTotal = useMemo(() => {
    return missingSourcesList.reduce((acc, s) => acc + s.confidence_penalty_pct, 0);
  }, [missingSourcesList]);

  // Base confidence is 88.4% (Chapala) adjusted by penalties
  const calculatedConfidence = useMemo(() => {
    const base = 88.4;
    const penalized = Math.max(45.0, base - confidencePenaltyTotal);
    return Number(penalized.toFixed(1));
  }, [confidencePenaltyTotal]);

  const currentStorm = useMemo(() => {
    const base = getCentralStormState(selectedStormId);
    const overrides = stormOverrides[selectedStormId] || {};
    return {
      ...base,
      ...overrides,
      observation_sources: observationSources,
      targeted_alerts: overrides.targeted_alerts || base.targeted_alerts,
      authorized_human_review: {
        ...base.authorized_human_review,
        ...(overrides.authorized_human_review || {}),
      },
    };
  }, [selectedStormId, stormOverrides, observationSources]);

  const selectStorm = useCallback((stormId: string) => {
    setSelectedStormId(stormId);
    setFusionSequence("idle");
    setFusionComplete(false);
    setAnalysisSequence("idle");
    setAnalysisComplete(false);
  }, []);

  // Toggle source status cycling: Available -> Missing -> Demo -> Available
  const toggleSourceStatus = useCallback((sourceId: string) => {
    setSourcesByStorm((prev) => {
      const current = prev[selectedStormId] || [...DEFAULT_OBSERVATION_SOURCES];
      const next = current.map((s) => {
        if (s.id !== sourceId) return s;
        let nextStatus: ObservationSourceItem["status"] = "Available";
        if (s.status === "Available") nextStatus = "Missing";
        else if (s.status === "Missing") nextStatus = "Demo";
        else nextStatus = "Available";
        return { ...s, status: nextStatus, is_active: nextStatus !== "Missing" };
      });
      return { ...prev, [selectedStormId]: next };
    });
  }, [selectedStormId]);

  const setSourceStatus = useCallback((sourceId: string, status: ObservationSourceItem["status"]) => {
    setSourcesByStorm((prev) => {
      const current = prev[selectedStormId] || [...DEFAULT_OBSERVATION_SOURCES];
      const next = current.map((s) =>
        s.id === sourceId ? { ...s, status, is_active: status !== "Missing" } : s
      );
      return { ...prev, [selectedStormId]: next };
    });
  }, [selectedStormId]);

  // Trigger Data Fusion sequence: Receiving -> Validating -> Aligning -> Fusing -> Complete
  const triggerFusion = useCallback(async () => {
    setIsFusing(true);
    setFusionComplete(false);

    setFusionSequence("receiving");
    await new Promise((r) => setTimeout(r, 400));

    setFusionSequence("validating");
    await new Promise((r) => setTimeout(r, 450));

    setFusionSequence("aligning");
    await new Promise((r) => setTimeout(r, 450));

    setFusionSequence("fusing");
    await new Promise((r) => setTimeout(r, 500));

    setFusionSequence("complete");
    setIsFusing(false);
    setFusionComplete(true);
  }, []);

  // Trigger AI Analysis sequence: Extracting -> Segmenting -> Inferring -> Complete
  const triggerAnalysis = useCallback(async () => {
    setIsAnalyzing(true);
    setAnalysisComplete(false);

    setAnalysisSequence("extracting");
    await new Promise((r) => setTimeout(r, 450));

    setAnalysisSequence("segmenting");
    await new Promise((r) => setTimeout(r, 500));

    setAnalysisSequence("inferring");
    await new Promise((r) => setTimeout(r, 550));

    setAnalysisSequence("complete");
    setIsAnalyzing(false);
    setAnalysisComplete(true);
  }, []);

  const authorizeAlert = useCallback(
    (alertId: string) => {
      setStormOverrides((prev) => {
        const storm = getCentralStormState(selectedStormId);
        const currentAlerts = (prev[selectedStormId]?.targeted_alerts || storm.targeted_alerts).map((a) =>
          a.alert_id === alertId ? { ...a, status: "AUTHORIZED_DISPATCHED" as const } : a
        );
        return {
          ...prev,
          [selectedStormId]: {
            ...prev[selectedStormId],
            targeted_alerts: currentAlerts,
          },
        };
      });
    },
    [selectedStormId]
  );

  const authorizeAllAlerts = useCallback(() => {
    setStormOverrides((prev) => {
      const storm = getCentralStormState(selectedStormId);
      const updatedAlerts = (prev[selectedStormId]?.targeted_alerts || storm.targeted_alerts).map((a) => ({
        ...a,
        status: "AUTHORIZED_DISPATCHED" as const,
      }));
      return {
        ...prev,
        [selectedStormId]: {
          ...prev[selectedStormId],
          targeted_alerts: updatedAlerts,
          authorized_human_review: {
            ...(prev[selectedStormId]?.authorized_human_review || storm.authorized_human_review),
            review_status: "OFFICIALLY_AUTHORIZED",
            authorization_signature: "DIGITALLY_SIGNED_BY_DUTY_OFFICER",
            review_timestamp_utc: new Date().toISOString(),
          },
        },
      };
    });
  }, [selectedStormId]);

  const updateHumanReview = useCallback(
    (notes: string, status: AuthorizedHumanReviewData["review_status"] = "OFFICIALLY_AUTHORIZED") => {
      setStormOverrides((prev) => {
        const storm = getCentralStormState(selectedStormId);
        const currentReview = prev[selectedStormId]?.authorized_human_review || storm.authorized_human_review;
        return {
          ...prev,
          [selectedStormId]: {
            ...prev[selectedStormId],
            authorized_human_review: {
              ...currentReview,
              review_status: status,
              meteorologist_notes: notes,
              authorization_signature: `DIGITALLY_AUTHORIZED_${Date.now()}`,
              review_timestamp_utc: new Date().toISOString(),
            },
          },
        };
      });
    },
    [selectedStormId]
  );

  const isFullyAuthorized = currentStorm.authorized_human_review.review_status === "OFFICIALLY_AUTHORIZED";

  return (
    <StormContext.Provider
      value={{
        currentStorm,
        selectStorm,
        availableStorms,
        observationSources,
        toggleSourceStatus,
        setSourceStatus,
        isFusing,
        fusionSequence,
        fusionComplete,
        triggerFusion,
        isAnalyzing,
        analysisSequence,
        analysisComplete,
        triggerAnalysis,
        calculatedConfidence,
        confidencePenaltyTotal,
        missingSourcesList,
        authorizeAlert,
        authorizeAllAlerts,
        updateHumanReview,
        isFullyAuthorized,
        activeTabStage,
        setActiveTabStage,
      }}
    >
      {children}
    </StormContext.Provider>
  );
}

export function useStorm() {
  const context = useContext(StormContext);
  if (!context) {
    throw new Error("useStorm must be used within a StormProvider");
  }
  return context;
}

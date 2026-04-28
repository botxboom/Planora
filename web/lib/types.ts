export type FeedbackVote = "up" | "down";
export type RetryStrategy =
  | "auto"
  | "transport_agent"
  | "stay_agent"
  | "activity_agent"
  | "optimizer_agent";

export type UserRequest = {
  query: string;
  user_id?: string;
};

export type TripDayPhase = "reaching" | "explore" | "return_home";

export type DailyItineraryDay = {
  phase?: TripDayPhase;
  headline?: string;
  primary_transport_summary?: string;
  getting_around?: string;
  stay_summary?: string;
  theme?: string;
  stay?: string;
  activities: string[];
  food: string[];
};

export type PlanState = {
  planner_output?: {
    destination: string;
    budget_inr: number;
    duration_days: number;
    preferences: string[];
  };
  final_itinerary?: {
    destination: string;
    duration_days: number;
    /** Inter-city leg only (origin → destination), not repeated as daily "flight". */
    arrival_summary?: string;
    daily_plan: Record<string, DailyItineraryDay>;
    budget_summary: Record<string, unknown>;
    optimization_notes: string[];
  };
  judge_output?: {
    score: number;
    issues: string[];
    improved_suggestions: string[];
    evaluation_summary: string;
  };
  refinement_count?: number;
  retry_target?: string;
  metadata?: {
    run_id?: string;
    parent_run_id?: string;
    retry_strategy?: string;
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

export type StreamEventName =
  | "run_started"
  | "planner_completed"
  | "agent_completed"
  | "aggregator_completed"
  | "judge_completed"
  | "retry_triggered"
  | "final_result"
  | "error"
  | "node_completed";

export type StreamEnvelope = {
  event: StreamEventName;
  data: Record<string, unknown>;
};

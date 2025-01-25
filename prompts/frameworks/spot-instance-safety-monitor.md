spot_safety_monitor:
  real_time_monitoring:
    instance_health:
      critical_metrics:
        - metric: "spot_interruption_warning"
          action: "immediate_checkpoint_and_migrate"
          threshold: "any"
        - metric: "job_failure_rate"
          action: "rollback_to_ondemand"
          threshold: "> 0.1%"
        - metric: "processing_delay"
          action: "alert_and_investigate"
          threshold: "> 10%"

    cost_monitoring:
      thresholds:
        - metric: "spot_price_spike"
          condition: "> 75% of on-demand"
          action: "evaluate_alternative_types"
        - metric: "total_cost"
          condition: "> projected_savings - 20%"
          action: "optimize_instance_selection"

  automated_response:
    interruption_handling:
      pre_interruption:
        - action: "checkpoint_state"
          timing: "immediately"
        - action: "drain_workload"
          timing: "within 60s"
        - action: "launch_replacement"
          timing: "within 30s"

      post_interruption:
        - action: "validate_state"
          timing: "immediately"
        - action: "restore_workload"
          timing: "within 120s"
        - action: "verify_processing"
          timing: "within 180s"

    failover_procedures:
      triggers:
        - condition: "multiple_interruptions"
          threshold: "3 in 1h"
          action: "switch_to_ondemand"
        - condition: "recovery_failure"
          threshold: "any"
          action: "switch_to_ondemand"
        - condition: "cost_above_threshold"
          threshold: "85% of ondemand"
          action: "reevaluate_strategy"

  safety_gates:
    migration_checks:
      pre_migration:
        - check: "backup_system_health"
          condition: "100% operational"
        - check: "failover_readiness"
          condition: "fully_configured"
        - check: "monitoring_active"
          condition: "all_metrics_reporting"

    operational_checks:
      continuous:
        - check: "job_success_rate"
          threshold: ">= 99.9%"
          window: "5m"
        - check: "processing_time"
          threshold: "<= baseline + 5%"
          window: "5m"
        - check: "cost_savings"
          threshold: ">= 40%"
          window: "1h"

  rollback_automation:
    triggers:
      immediate:
        - condition: "job_failure_rate > 0.1%"
          window: "5m"
        - condition: "processing_delay > 15%"
          window: "15m"
        - condition: "cost_savings < 30%"
          window: "1h"

    procedures:
      - step: "pause_new_spot_requests"
        timing: "immediate"
      - step: "launch_ondemand_instances"
        timing: "within 30s"
      - step: "migrate_workload"
        timing: "within 90s"
      - step: "verify_stability"
        timing: "within 180s"
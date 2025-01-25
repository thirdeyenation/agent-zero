resource_optimization:
  analysis_phase:
    resource_audit:
      metrics_collection:
        compute:
          - cpu_utilization:
              peak: "95th percentile"
              average: "median over 2 weeks"
              low: "5th percentile"
          - memory_usage:
              peak: "95th percentile"
              average: "median over 2 weeks"
              committed: "actual allocated"
          - network_io:
              bandwidth_usage
              packet_rate
              connection_count
        storage:
          - iops_utilization
          - throughput_usage
          - storage_growth_rate
        
      time_periods:
        - business_hours: "9am-5pm weekdays"
        - peak_hours: "identified high-load periods"
        - off_hours: "nights and weekends"
        - seasonal_patterns: "monthly/quarterly peaks"

  optimization_actions:
    immediate_adjustments:
      compute_instances:
        - identify_oversized:
            criteria:
              - cpu_usage: "< 20% for 80% of time"
              - memory_usage: "< 30% for 80% of time"
              - network_usage: "< 10% of provisioned"
        - right_sizing_recommendations:
            rules:
              - down_size: "if peak usage < 50% for 2 weeks"
              - up_size: "if peak usage > 80% for 1 week"
              - instance_family: "evaluate cost-effective alternatives"

      container_resources:
        - analyze_limits:
            metrics:
              - actual_cpu_usage
              - actual_memory_usage
              - peak_resource_needs
        - adjust_resources:
            strategy:
              - set_requests: "based on p50 usage"
              - set_limits: "based on p95 usage"
              - include_headroom: "20% above p95"

    autoscaling_optimization:
      horizontal_scaling:
        metrics:
          - cpu_utilization: "target 70%"
          - memory_utilization: "target 75%"
          - request_count: "per instance"
        thresholds:
          scale_out: "80% utilization for 5 minutes"
          scale_in: "50% utilization for 15 minutes"
      
      vertical_scaling:
        rules:
          - upsize_trigger: "90% utilization for 10 minutes"
          - downsize_trigger: "40% utilization for 1 hour"
          - cooldown_period: "15 minutes between adjustments"

  implementation_plan:
    phases:
      1_analysis:
        - duration: "1 week"
        - activities:
            - collect_baseline_metrics
            - analyze_usage_patterns
            - identify_optimization_targets
            - create_adjustment_plan
      
      2_non_prod_implementation:
        - duration: "3 days"
        - activities:
            - adjust_development_environments
            - monitor_impact
            - collect_feedback
            - refine_approach
      
      3_prod_implementation:
        - duration: "1 week"
        - activities:
            - implement_by_priority
            - monitor_closely
            - validate_performance
            - document_changes

  monitoring_framework:
    metrics_tracking:
      performance:
        - response_times
        - error_rates
        - resource_utilization
        - application_metrics
      
      cost:
        - pre_optimization_baseline
        - post_optimization_costs
        - savings_calculation
        - resource_efficiency

    alerts:
      performance_degradation:
        - response_time_increase: "> 10%"
        - error_rate_increase: "> 5%"
        - resource_saturation: "> 85%"
      
      cost_anomalies:
        - sudden_cost_increase: "> 20%"
        - resource_usage_spike: "> 30%"
        - unexpected_scaling_events

  rollback_procedures:
    triggers:
      - performance_degradation: "sustained for 15 minutes"
      - error_rate_increase: "> 10% for 5 minutes"
      - business_impact: "any significant impact"
    
    process:
      1: "Revert resource configurations"
      2: "Validate system stability"
      3: "Analyze root cause"
      4: "Adjust optimization strategy"
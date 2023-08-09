def azure_kpi_metrics(experiment_name, teams_webhook_url) -> None:

    """
    Calculates and sends key performance indicator (KPI) metrics to a Microsoft Teams channel

    Args:
        experiment_name (str): Name of current experiment
        teams_webhook_url (str): Incoming Webhook Connetor URL from Microsft Teams channel
    """


    # Import required libraries

    import azure.functions as func
    from azureml.core import Workspace, Experiment
    import pandas as pd
    import numpy as np
    import pymsteams



    # Create a connection to an AML workspace and an experiment within that workspace

    ws: Workspace = Workspace.from_config()

    work_space: Workspace = Workspace.get(
        name = ws.name,
        subscription_id = ws.subscription_id,
        resource_group = ws.resource_group
        )

    experiment = Experiment(
        workspace = work_space,
        name = experiment_name
        )



    # Retrieve a list of runs in the given experiment using the `get_runs()` method

    runs_list = list(experiment.get_runs())

    

    current_run: Run = runs_list[0]     # First element in the list of runs corresponds to the current/latest run
    current_run_metrics = current_run.get_metrics()     # Obtain the metrics of the current/latest run



    # Check if there are at least two runs in the `runs_list` variable. 

    if len(runs_list) < 2:
        # If there are less than two runs, it means that there is no previous run to compare metrics with. 
        # Hence set`previous_run_metrics` dictionary to an empty dictionary `{}`.
        previous_run_metrics = {}
    
    else:
        # If a previous run exists, it is the second element of the `run_list`, for which the metrics are obtained.
        previous_run: Run = runs_list[1]
        previous_run_metrics = previous_run.get_metrics()
    


    # Check if there are any metric names in the previous run metrics that are not present in the current run metrics. 
    # If there are, add those metric names to the current run metrics dictionary with a NaN value.

    for a in previous_run_metrics.keys():
        if a not in current_run_metrics.keys():
            current_run_metrics[a] = None

    

    # Check if there are any metric names in the current run metrics that are not present in the previous run metrics. 
    # If there are, add those metric names to the previous run metrics dictionary with a NaN value.

    for a in current_run_metrics.keys():
        if a not in previous_run_metrics.keys():
            previous_run_metrics[a] = None
      
            
    
    # Sort keys of both dictionaries in same order to perform the comparison
    
    result_dict = current_run_metrics.copy()
    for key in result_dict:
        result_dict[key] = previous_run_metrics[key]
    previous_run_metrics = result_dict
    


    # Add metrics values of current and previous runs into a list

    current_run_metrics_list = list(current_run_metrics.values())
    previous_run_metrics_list = list(previous_run_metrics.values())



    # Create a dictionary called `metric_dict` to store the metric names, previous run values, and current run values for the KPI metrics

    metric_dict = {}
    metric_dict['Metric Name'] = list(current_run_metrics.keys())
    metric_dict['Previous Run Value'] = previous_run_metrics_list
    metric_dict['Current Run Value'] = current_run_metrics_list



    # Convert `metric_dict` dictionary it into a DataFrame

    metrics_df: DataFrame = pd.DataFrame.from_dict(metric_dict)



    # Define conditions to check if there are any changes in metric values

    conditions = [
        metrics_df['Previous Run Value'] > metrics_df['Current Run Value'], 
        metrics_df['Previous Run Value'] < metrics_df['Current Run Value'],
        metrics_df['Previous Run Value'] == metrics_df['Current Run Value']
        ]
                    
    choices: list[str] = [
        'Decrease in metric value',
        'Increase in metric value',
        'No Change'
        ]



    # Replace `str` comparisons between logs with NA

    metrics_df['Comparison'] = np.select(conditions, choices, default='NA')
    for index, row in metrics_df.iterrows():
        if isinstance(row['Previous Run Value'], str) or isinstance(row['Current Run Value'], str):
            metrics_df.at[index, 'Comparison'] = 'NA'
    
    
    
    # Create a connection to a Microsoft Teams channel using the `pymsteams` library, using Incoming Webhook Connector URL
    teams_connection = pymsteams.connectorcard(teams_webhook_url)



    # Convert dataframe to html before senidng it to Microsoft Teams
    teams_connection.text(metrics_df.to_html(index=False))



    # Button to open the Jobs page on AML to manually register the model
    register_url = current_run.get_portal_url()
    teams_connection.addLinkButton("Register Model", register_url)
    teams_connection.send()

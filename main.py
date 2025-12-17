import xmltodict
import statistics
import argparse
from pathlib import Path

def parse_jasome_xml(xml_file_path):
    # Read and parse XML file
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    
    data = xmltodict.parse(xml_content)
    
    # Initialize metrics storage
    metrics = {
        'mccabe_cyclomatic_complexity': [],
        'system_complexity': [],
        'data_complexity': [],
        'total_lines_of_code': []
    }
    
    # Navigate through XML hierarchy to reach Method nodes
    # Structure: Project -> Package -> Class -> Method
    def extract_method_metrics(node):
        if isinstance(node, dict):
            # Check if this is a Method node
            if 'Method' in node:
                methods = node['Method']
                # Handle both single method and list of methods
                if not isinstance(methods, list):
                    methods = [methods]
                
                for method in methods:
                    # Extract metrics from the Metrics node inside each method
                    if 'Metrics' in method and 'Metric' in method['Metrics']:
                        method_metrics = method['Metrics']['Metric']
                        # Handle both single metric and list of metrics
                        if not isinstance(method_metrics, list):
                            method_metrics = [method_metrics]
                        
                        for metric in method_metrics:
                            metric_name = metric.get('@name', '')
                            metric_value = metric.get('@value', '0')
                            
                            if metric_name == 'VG':  # McCabe Cyclomatic Complexity
                                metrics['mccabe_cyclomatic_complexity'].append(
                                    float(metric_value)
                                )
                            elif metric_name == 'Ci':  # System Complexity
                                metrics['system_complexity'].append(
                                    float(metric_value)
                                )
                            elif metric_name == 'Di':  # Data Complexity
                                metrics['data_complexity'].append(
                                    float(metric_value)
                                )
                            elif metric_name == 'TLOC':  # Total Lines of Code
                                metrics['total_lines_of_code'].append(
                                    float(metric_value)
                                )
            
            # Recursively process all child nodes
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    extract_method_metrics(value)
                    
        elif isinstance(node, list):
            for item in node:
                extract_method_metrics(item)
    
    # Start extraction from root
    extract_method_metrics(data)
    
    # Calculate averages
    results = {
        'total_methods': len(metrics['mccabe_cyclomatic_complexity']),
        'avg_mccabe_cyclomatic_complexity': 0,
        'avg_system_complexity': 0,
        'avg_data_complexity': 0,
        'avg_total_lines_of_code': 0
    }
    
    if results['total_methods'] > 0:
        results['avg_mccabe_cyclomatic_complexity'] = (
            sum(metrics['mccabe_cyclomatic_complexity']) / 
            len(metrics['mccabe_cyclomatic_complexity'])
        )
        results['avg_system_complexity'] = (
            sum(metrics['system_complexity']) / 
            len(metrics['system_complexity'])
        )
        results['avg_data_complexity'] = (
            sum(metrics['data_complexity']) / 
            len(metrics['data_complexity'])
        )
        results['avg_total_lines_of_code'] = (
            sum(metrics['total_lines_of_code']) / 
            len(metrics['total_lines_of_code'])
        )
    
    return results, metrics

def display_results(results, metrics):
    print("=" * 60)
    print("JASOME METRICS ANALYSIS - AVERAGE ACROSS METHODS")
    print("=" * 60)
    print(f"\nTotal Methods Analyzed: {results['total_methods']}")
    print("\n" + "-" * 60)
    print("AVERAGE METRICS:")
    print("-" * 60)
    print(f"McCabe Cyclomatic Complexity: {results['avg_mccabe_cyclomatic_complexity']:.2f}")
    print(f"System Complexity:            {results['avg_system_complexity']:.2f}")
    print(f"Data Complexity:              {results['avg_data_complexity']:.2f}")
    print(f"Total Lines of Code (TLOC):   {results['avg_total_lines_of_code']:.2f}")
    print("=" * 60)
    
    # Additional statistics
    if results['total_methods'] > 0:
        print("\nADDITIONAL STATISTICS:")
        print("-" * 60)
        
        for metric_name, metric_values in metrics.items():
            if metric_values:
                readable_name = metric_name.replace('_', ' ').title()
                print(f"\n{readable_name}:")
                print(f"  Min:    {min(metric_values):.2f}")
                print(f"  Max:    {max(metric_values):.2f}")
                print(f"  Median: {statistics.median(metric_values):.2f}")
                print(f"  StdDev: {statistics.stdev(metric_values):.2f}" 
                      if len(metric_values) > 1 else "  StdDev: N/A")

def main():
    parser = argparse.ArgumentParser(
        description="Parse Jasome XML metrics and compute averages."
    )
    
    parser.add_argument(
        "xml",
        help="Path to the Jasome XML file (e.g., output.xml)"
    )
    
    args = parser.parse_args()
    xml_file = Path(args.xml)

    
    # Check file exists
    if not xml_file.exists():
        print(f"Error: XML file '{xml_file}' not found!\n")
        print("Example usage:")
        print("  python metrics.py output.xml")
        print("  python metrics.py /path/to/output.xml\n")
        return

    try:
        results, metrics = parse_jasome_xml(str(xml_file))
        display_results(results, metrics)

    except Exception as e:
        print(f"Error processing XML file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

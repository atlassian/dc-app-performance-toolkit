from util.jtl_convertor.jtl_validator import SUPPORTED_JTL_HEADER, GRP_THREADS, ALL_THREADS
from csv import DictWriter, DictReader
from pathlib import Path


# https://github.com/Blazemeter/taurus/pull/1311
def reorder_kpi_jtl(file_path, output_dir):
    updated_row = []
    with file_path.open(mode='r') as kpi:
        reader = DictReader(kpi)
        usupported_headers = list(set(reader.fieldnames) - set(SUPPORTED_JTL_HEADER))
        for row in reader:
            for unsupported_header in usupported_headers:
                if unsupported_header in row.keys():
                    del row[unsupported_header]
            if GRP_THREADS not in row.keys():
                row[GRP_THREADS] = row[ALL_THREADS]
            updated_row.append(row)
    output_file = Path(output_dir) / 'kpi.jtl'
    with output_file.open(mode='a') as out_kpi:
        writer = DictWriter(out_kpi, fieldnames=SUPPORTED_JTL_HEADER)
        writer.writeheader()
        for row in updated_row:
            writer.writerow(row)
    return output_file

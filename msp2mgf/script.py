import re
import sys
from tqdm import tqdm  # Import tqdm for the progress bar functionality

def parse_msp_entry(entry):
    compound = {}
    peaks = []
    lines = entry.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            compound[key.strip()] = value.strip()
        else:
            parts = re.split(r'\s+', line.strip())
            if len(parts) == 2:
                try:
                    mz, intensity = float(parts[0]), float(parts[1])
                    peaks.append(f"{mz}\t{intensity}")
                except ValueError:
                    continue  # Skip lines that do not contain valid peak data
    return compound, peaks

def write_line_if_not_na(outfile, key, value):
    if value != 'N/A':
        outfile.write(f"{key}={value}\n")

def convert_msp_to_mgf(input_msp_filename, output_mgf_filename):
    with open(input_msp_filename, 'r') as file:
        entries = file.read().strip().split('\n\n')

    print(f"Converting {len(entries)} entries from {input_msp_filename} to {output_mgf_filename}")

    with open(output_mgf_filename, 'w') as outfile:
        file_index = 1

        # Add a tqdm progress bar
        for entry in tqdm(entries, desc="Processing entries", unit="entry"):
            compound, peaks = parse_msp_entry(entry)
            
            outfile.write("BEGIN IONS\n")
            write_line_if_not_na(outfile, "PEPMASS", compound.get('PrecursorMZ', 'N/A'))
            outfile.write("CHARGE=1+\n")
            outfile.write("MSLEVEL=2\n")
            write_line_if_not_na(outfile, "TITLE", compound.get('Notes', 'N/A'))
            outfile.write(f"FILENAME=Training_{file_index:03}.mgf\n")
            outfile.write("SEQ=*..*\n")
            write_line_if_not_na(outfile, "IONMODE", compound.get('Ion_mode', 'N/A'))
            write_line_if_not_na(outfile, "NAME", f"{compound.get('Name', 'N/A')} {compound.get('Precursor_type', '')}".strip())
            write_line_if_not_na(outfile, "SMILES", compound.get('SMILES', 'N/A'))
            write_line_if_not_na(outfile, "INCHI", compound.get('InChIKey', 'N/A'))
            write_line_if_not_na(outfile, "FORMULA", compound.get('Formula', 'N/A'))
            write_line_if_not_na(outfile, "CASNO", compound.get('CASNO', 'N/A'))
            write_line_if_not_na(outfile, "COLLISIONENERGY", compound.get('Collision_energy', 'N/A'))
            try:
                comment_info = compound.get('Comment', '').split(';')
                spectrum_id = comment_info[0].split('=')[1] if '=' in comment_info[0] else "N/A"
                write_line_if_not_na(outfile, "SPECTRUMID", spectrum_id)
            except IndexError:
                outfile.write("SPECTRUMID=N/A\n")
            outfile.write(f"SCANS={file_index}\n")
            for peak in peaks:
                outfile.write(f"{peak}\n")
            outfile.write("END IONS\n\n\n")
            
            file_index += 1
    
    print("Conversion complete. The MGF file has been written.")

# Example usage
if __name__ == "__main__":
    input_msp_filename = sys.argv[1] if len(sys.argv) > 1 else 'input.msp'
    output_mgf_filename = sys.argv[2] if len(sys.argv) > 2 else 'output.mgf'
    convert_msp_to_mgf(input_msp_filename, output_mgf_filename)

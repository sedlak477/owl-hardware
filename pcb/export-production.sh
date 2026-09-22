#!/usr/bin/env bash
# Regenerates pcb/<board>/production/{generic,jlcpcb} from the KiCad sources.
#
# Requires:
#   - kicad-cli (KiCad 10)
#   - the KiCad "Fabrication Toolkit" plugin (bennymeg/Fabrication-Toolkit) for the JLCPCB files,
#     run with the Python interpreter KiCad uses (it needs the pcbnew and wx modules)
#
# Usage: pcb/export-production.sh [board...]    e.g. pcb/export-production.sh stator
set -euo pipefail

PCB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KICAD_PYTHON="${KICAD_PYTHON:-python3}"
PLUGIN_DIR="${FABRICATION_TOOLKIT_DIR:-$HOME/.local/share/kicad/10.0/3rdparty/plugins}"
PLUGIN_MODULE="com_github_bennymeg_JLC-Plugin-for-KiCad"

GERBER_LAYERS="F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts"
BOM_FIELDS='Reference,${QUANTITY},Value,Footprint,Manufacturer,MPN,LCSC'
BOM_LABELS='Designator,Quantity,Value,Footprint,Manufacturer,MPN,LCSC'
BOM_GROUP_BY='Value,Footprint,Manufacturer,MPN,LCSC'

# board name -> KiCad project path (without extension), relative to pcb/
declare -A BOARDS=(
  [controller]="controller/src/OWL - Rotor v2"
  [stator]="stator/src/Stator"
  [sensor-ma600a]="sensor/ma600a/src/Sensor - MA600A"
)

zip_directory() {
  local source_dir="$1" archive="$2"
  (cd "$source_dir" && "$KICAD_PYTHON" -m zipfile -c "$archive" *)
}

export_generic() {
  local name="$1" project="$2" output_dir="$3" work_dir="$4"
  local gerber_dir="$work_dir/generic-gerbers"
  mkdir -p "$gerber_dir" "$output_dir"

  kicad-cli pcb export gerbers --layers "$GERBER_LAYERS" -o "$gerber_dir/" "$project.kicad_pcb"
  kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-separate-th \
    --generate-map --map-format gerberx2 -o "$gerber_dir/" "$project.kicad_pcb"
  zip_directory "$gerber_dir" "$output_dir/$name-gerbers.zip"

  kicad-cli pcb export ipcd356 -o "$output_dir/$name-netlist.ipc" "$project.kicad_pcb"
  kicad-cli pcb export pos --format csv --units mm --side both --exclude-dnp \
    -o "$output_dir/$name-positions.csv" "$project.kicad_pcb"
  kicad-cli sch export bom --fields "$BOM_FIELDS" --labels "$BOM_LABELS" --group-by "$BOM_GROUP_BY" \
    --ref-range-delimiter '' --exclude-dnp -o "$output_dir/$name-bom.csv" "$project.kicad_sch"
}

export_jlcpcb() {
  local name="$1" project="$2" output_dir="$3" work_dir="$4"
  # The toolkit always writes to <project dir>/production, so run it on a copy of src/.
  local project_copy="$work_dir/jlcpcb-src"
  cp -r "$(dirname "$project")" "$project_copy"
  rm -rf "$project_copy/production"
  local board_copy="$project_copy/$(basename "$project").kicad_pcb"

  "$KICAD_PYTHON" - "$PLUGIN_DIR" "$PLUGIN_MODULE" "$board_copy" <<'EOF'
import runpy
import sys

plugin_dir, plugin_module, board = sys.argv[1:4]
sys.path.insert(0, plugin_dir)
sys.argv = ["cli", "--path", board, "--autoTranslate", "--autoFill", "--excludeDNP", "--nonInteractive", "--noBackup"]
runpy.run_module(f"{plugin_module}.cli", run_name="__main__")
EOF

  local toolkit_output="$project_copy/production"
  local gerber_archives=("$toolkit_output"/*.zip)
  [[ ${#gerber_archives[@]} -eq 1 && -f ${gerber_archives[0]} ]] || { echo "No JLCPCB Gerber archive for $name" >&2; exit 1; }
  mkdir -p "$output_dir"
  mv "${gerber_archives[0]}" "$output_dir/$name-gerbers.zip"
  mv "$toolkit_output/bom.csv" "$output_dir/$name-bom.csv"
  mv "$toolkit_output/positions.csv" "$output_dir/$name-positions.csv"
}

export_board() {
  local name="$1"
  local project="$PCB_DIR/${BOARDS[$name]}"
  local production_dir; production_dir="$(dirname "$(dirname "$project")")/production"
  local work_dir; work_dir="$(mktemp -d)"
  trap 'rm -rf "$work_dir"' RETURN

  echo "== $name"
  rm -rf "$production_dir/generic" "$production_dir/jlcpcb"
  export_generic "$name" "$project" "$production_dir/generic" "$work_dir"
  export_jlcpcb "$name" "$project" "$production_dir/jlcpcb" "$work_dir"
}

selected_boards=("$@")
[[ ${#selected_boards[@]} -gt 0 ]] || selected_boards=("${!BOARDS[@]}")
for board in "${selected_boards[@]}"; do
  [[ -v BOARDS[$board] ]] || { echo "Unknown board '$board'. Known: ${!BOARDS[*]}" >&2; exit 1; }
  export_board "$board"
done

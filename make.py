#!/usr/bin/env python
import os
import pathlib
import sys
import shutil
import cfru.scripts.make
import dpe.scripts.make
import ips_util.ips_util as ips_util


def main():
    top_dir = pathlib.Path(__file__).parent
    base_rom_path = top_dir / "BPRE0.gba"
    dpe_path = top_dir / "dpe"
    dpe_input_rom_path = dpe_path / "BPRE0.gba"

    ips_dir = top_dir / "ips_patches"
    ips_patches = []
    for ips_file in ips_dir.iterdir():
        if ips_file.name.endswith('.ips'):
            ips_patches.append(ips_util.Patch.load(ips_file))
    # apply ips patches and output to dpe input rom path
    with open(base_rom_path, "rb") as in_file:
        with open(dpe_input_rom_path, "wb") as out_file:
            data = in_file.read()
            for patch in ips_patches:
                data = patch.apply(data)
            out_file.write(data)

    dpe_output_rom_path = dpe_path / "test.gba"
    try:
        os.remove(dpe_output_rom_path)
    except FileNotFoundError:
        pass
    os.chdir(dpe_path)
    dpe.scripts.make.main()

    cfru_path = top_dir / "cfru"
    cfru_input_rom_path = cfru_path / "BPRE0.gba"
    try:
        shutil.copyfile(dpe_output_rom_path, cfru_input_rom_path)
    except FileNotFoundError:
        # DPE must have failed to create the file. It does not raise an
        # exception for us to catch (nor exit non-zero) in failure cases, so we
        # must catch it this way.
        sys.exit("ERROR: DPE failed to output")

    os.chdir(cfru_path)
    cfru.scripts.make.main()

    cfru_output_rom_path = cfru_path / "test.gba"
    final_output_rom_path = top_dir / "test.gba"
    try:
        shutil.copyfile(cfru_output_rom_path, final_output_rom_path)
    except FileNotFoundError:
        sys.exit("ERROR: CFRU failed to output")


if __name__ == "__main__":
    main()

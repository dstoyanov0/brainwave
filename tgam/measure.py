import mne
import click

from TGAMpy.TGAMpy import TGAM

@click.command()
@click.option("--port", help="COM Port for TGAM")
def main(port: str):
    """1 Channel EEG exporter for TGAM"""
    module = TGAM()
    module.connect(port, timeout=5)


if __name__ == "__main__":
    main()
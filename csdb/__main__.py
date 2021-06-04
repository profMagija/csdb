import click

@click.group()
def cli():
    pass

@cli.command('serve')
@click.option('--db', default=None, type=click.Path(exists=True))
@click.option('--mem', default=False, is_flag=True)
@click.option('--host', default=None, type=str)
@click.option('--port', default=None, type=int)
def serve(db, mem, host, port):
    if not db and not mem:
        raise click.BadArgumentUsage('either --db or --mem must be supplied')
    from . import serving
    serving.serve(db, host=host, port=port)

cli()
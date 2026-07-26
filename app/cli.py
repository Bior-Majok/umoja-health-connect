import uuid
import click
from app import db
from app.models.admin import Administrator


def register_cli(app):
    @app.cli.command('seed-admin')
    @click.option('--full-name', prompt=True)
    @click.option('--phone-number', prompt=True)
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option('--scope-level', default='national', type=click.Choice(['national', 'regional']))
    @click.option('--region', default=None)
    def seed_admin(full_name, phone_number, password, scope_level, region):
        """Provision an Administrator account (admins are not self-registered)."""
        if Administrator.query.filter_by(phone_number=phone_number).first():
            click.echo('An administrator with that phone number already exists.')
            return

        admin = Administrator(
            admin_id=str(uuid.uuid4())[:8].upper(),
            full_name=full_name,
            phone_number=phone_number,
            scope_level=scope_level,
            region=region,
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Administrator created: {admin.admin_id}')

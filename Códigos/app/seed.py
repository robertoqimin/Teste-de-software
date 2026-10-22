"""Cria contas sem excluir ou substituir usuários existentes."""
import argparse
import getpass
from werkzeug.security import generate_password_hash
from app import create_app
from app.database import get_session
from app.models import UsuarioModel


def run_seed(email=None, senha=None, tipo='admin'):
    email = email or ('gestor@escola.com' if tipo == 'admin' else None)
    if not email or not senha:
        raise ValueError('Informe o e-mail e a senha da nova conta.')
    if tipo == 'admin' and len(senha) < 8:
        raise ValueError('A senha do administrador deve ter pelo menos 8 caracteres.')
    create_app()
    with get_session() as db:
        if db.query(UsuarioModel).filter_by(email=email).first():
            print('Conta já existente; dados preservados.')
            return
        db.add(UsuarioModel(email=email, senha=generate_password_hash(senha), tipo=tipo))
        db.commit()
    print(f'Conta {tipo} criada: {email}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    roles = parser.add_mutually_exclusive_group()
    roles.add_argument('--admin', action='store_true', help='Criar administrador (padrão).')
    roles.add_argument('--secretaria', action='store_true', help='Criar secretaria com --email.')
    parser.add_argument('--email')
    args = parser.parse_args()
    if args.secretaria and not args.email:
        parser.error('--secretaria exige --email.')
    tipo = 'secretaria' if args.secretaria else 'admin'
    run_seed(email=args.email, senha=getpass.getpass('Senha da nova conta: '), tipo=tipo)

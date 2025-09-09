#!/usr/bin/env python3
"""
Helper to obtain a Cognito id_token for testing protected API routes.

What it does:
- Ensures a public App Client exists with USER_PASSWORD_AUTH enabled (creates if missing)
- Ensures a test user exists (creates and sets a permanent password if needed)
- Initiates USER_PASSWORD_AUTH to get an id_token

Usage (PowerShell):
  python scripts/get-cognito-id-token.py --pool-id us-east-1_ID7e0JI2c \
      --region us-east-1 --username testuser@example.com --password "StrongPwd123!" \
      [--client-id <existing_client_id>]

Prints the id_token to stdout.
"""
import argparse
import sys
import json
import boto3
from botocore.exceptions import ClientError, BotoCoreError


def ensure_app_client(cognito, user_pool_id: str, client_id: str | None, region: str) -> str:
    if client_id:
        return client_id

    # Try to find an existing public client with password auth enabled
    paginator = cognito.get_paginator("list_user_pool_clients")
    for page in paginator.paginate(UserPoolId=user_pool_id, MaxResults=60):
        for c in page.get("UserPoolClients", []):
            cid = c.get("ClientId")
            try:
                d = cognito.describe_user_pool_client(UserPoolId=user_pool_id, ClientId=cid)[
                    "UserPoolClient"
                ]
                if not d.get("ClientSecret") and (
                    "ALLOW_USER_PASSWORD_AUTH" in d.get("ExplicitAuthFlows", [])
                ):
                    return cid
            except (ClientError, BotoCoreError):
                continue

    # Create a fresh public app client suitable for CLI testing
    name = "voice-assistant-ai-cli"
    resp = cognito.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=name,
        GenerateSecret=False,
        ExplicitAuthFlows=[
            "ALLOW_USER_PASSWORD_AUTH",
            "ALLOW_REFRESH_TOKEN_AUTH",
        ],
        PreventUserExistenceErrors="ENABLED",
    )
    return resp["UserPoolClient"]["ClientId"]


def ensure_user(cognito, user_pool_id: str, username: str, password: str) -> None:
    try:
        cognito.admin_get_user(UserPoolId=user_pool_id, Username=username)
        return
    except cognito.exceptions.UserNotFoundException:
        pass

    # Create user with a temporary password then set a permanent password
    try:
        cognito.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            TemporaryPassword=password,
            MessageAction="SUPPRESS",
        )
    except ClientError as e:
        if e.response["Error"].get("Code") != "UsernameExistsException":
            raise

    cognito.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=username,
        Password=password,
        Permanent=True,
    )


def get_id_token(cognito, client_id: str, username: str, password: str) -> str:
    resp = cognito.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
    )
    return resp["AuthenticationResult"]["IdToken"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool-id", required=True, help="Cognito User Pool ID")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--client-id", default=None, help="Existing App Client ID (optional)")
    args = parser.parse_args()

    cognito = boto3.client("cognito-idp", region_name=args.region)

    try:
        client_id = ensure_app_client(cognito, args.pool_id, args.client_id, args.region)
        ensure_user(cognito, args.pool_id, args.username, args.password)
        token = get_id_token(cognito, client_id, args.username, args.password)
        print(token)
        return 0
    except (ClientError, BotoCoreError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())



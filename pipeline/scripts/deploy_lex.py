#!/usr/bin/env python3
"""
Amazon Lex Bot Deployment Script
Deploys and configures Lex bot for Voice Assistant AI
"""

import json
import time
import argparse
import boto3
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LexBotDeployer:
    """Handles Amazon Lex bot deployment and configuration"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.lex_client = boto3.client('lexv2-models', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        
    def create_or_update_bot(self, bot_config: Dict[str, Any]) -> str:
        """Create or update Lex bot"""
        bot_name = bot_config['botName']
        
        try:
            # Check if bot exists
            response = self.lex_client.describe_bot(botId=bot_name)
            bot_id = response['botId']
            logger.info(f"Bot {bot_name} exists, updating...")
            
            # Update bot
            self.lex_client.update_bot(
                botId=bot_id,
                botName=bot_config['botName'],
                description=bot_config['description'],
                roleArn=bot_config['roleArn'],
                dataPrivacy=bot_config['dataPrivacy'],
                idleSessionTTLInSeconds=bot_config['idleSessionTTLInSeconds']
            )
            
        except self.lex_client.exceptions.ResourceNotFoundException:
            logger.info(f"Bot {bot_name} does not exist, creating...")
            
            # Create bot
            response = self.lex_client.create_bot(
                botName=bot_config['botName'],
                description=bot_config['description'],
                roleArn=bot_config['roleArn'],
                dataPrivacy=bot_config['dataPrivacy'],
                idleSessionTTLInSeconds=bot_config['idleSessionTTLInSeconds'],
                botTags=bot_config.get('botTags', {}),
                testBotAliasTags=bot_config.get('testBotAliasTags', {})
            )
            bot_id = response['botId']
        
        logger.info(f"Bot operation completed. Bot ID: {bot_id}")
        return bot_id
    
    def create_or_update_bot_locale(self, bot_id: str, locale_config: Dict[str, Any]) -> None:
        """Create or update bot locale"""
        locale_id = locale_config['localeId']
        
        try:
            # Check if locale exists
            self.lex_client.describe_bot_locale(
                botId=bot_id,
                botVersion='DRAFT',
                localeId=locale_id
            )
            logger.info(f"Locale {locale_id} exists, updating...")
            
            # Update locale
            self.lex_client.update_bot_locale(
                botId=bot_id,
                botVersion='DRAFT',
                localeId=locale_id,
                description=locale_config['description'],
                nluIntentConfidenceThreshold=locale_config['nluIntentConfidenceThreshold'],
                voiceSettings=locale_config.get('voiceSettings', {})
            )
            
        except self.lex_client.exceptions.ResourceNotFoundException:
            logger.info(f"Locale {locale_id} does not exist, creating...")
            
            # Create locale
            self.lex_client.create_bot_locale(
                botId=bot_id,
                botVersion='DRAFT',
                localeId=locale_id,
                description=locale_config['description'],
                nluIntentConfidenceThreshold=locale_config['nluIntentConfidenceThreshold'],
                voiceSettings=locale_config.get('voiceSettings', {})
            )
        
        logger.info(f"Locale {locale_id} operation completed")
    
    def create_slot_types(self, bot_id: str, locale_id: str, slot_types: List[Dict[str, Any]]) -> None:
        """Create slot types"""
        for slot_type in slot_types:
            slot_type_name = slot_type['slotTypeName']
            
            try:
                # Check if slot type exists
                self.lex_client.describe_slot_type(
                    botId=bot_id,
                    botVersion='DRAFT',
                    localeId=locale_id,
                    slotTypeId=slot_type_name
                )
                logger.info(f"Slot type {slot_type_name} exists, updating...")
                
                # Update slot type
                self.lex_client.update_slot_type(
                    botId=bot_id,
                    botVersion='DRAFT',
                    localeId=locale_id,
                    slotTypeId=slot_type_name,
                    slotTypeName=slot_type['slotTypeName'],
                    description=slot_type.get('description', ''),
                    slotTypeValues=slot_type.get('slotTypeValues', []),
                    valueSelectionStrategy=slot_type.get('valueSelectionStrategy', 'ORIGINAL_VALUE')
                )
                
            except self.lex_client.exceptions.ResourceNotFoundException:
                logger.info(f"Slot type {slot_type_name} does not exist, creating...")
                
                # Create slot type
                self.lex_client.create_slot_type(
                    botId=bot_id,
                    botVersion='DRAFT',
                    localeId=locale_id,
                    slotTypeName=slot_type['slotTypeName'],
                    description=slot_type.get('description', ''),
                    slotTypeValues=slot_type.get('slotTypeValues', []),
                    valueSelectionStrategy=slot_type.get('valueSelectionStrategy', 'ORIGINAL_VALUE')
                )
            
            logger.info(f"Slot type {slot_type_name} operation completed")
    
    def create_intents(self, bot_id: str, locale_id: str, intents: List[Dict[str, Any]], lambda_arn: str) -> None:
        """Create intents"""
        for intent in intents:
            intent_name = intent['intentName']
            
            try:
                # Check if intent exists
                self.lex_client.describe_intent(
                    botId=bot_id,
                    botVersion='DRAFT',
                    localeId=locale_id,
                    intentId=intent_name
                )
                logger.info(f"Intent {intent_name} exists, updating...")
                
                # Update intent
                self.lex_client.update_intent(
                    botId=bot_id,
                    botVersion='DRAFT',
                    localeId=locale_id,
                    intentId=intent_name,
                    intentName=intent['intentName'],
                    description=intent.get('description', ''),
                    sampleUtterances=intent.get('sampleUtterances', []),
                    slots=intent.get('slots', []),
                    fulfillmentCodeHook={
                        'enabled': True,
                        'fulfillmentUpdatesSpecification': {
                            'active': False
                        }
                    } if lambda_arn else {'enabled': False}
                )
                
            except self.lex_client.exceptions.ResourceNotFoundException:
                logger.info(f"Intent {intent_name} does not exist, creating...")
                
                # Create intent
                self.lex_client.create_intent(
                    botId=bot_id,
                    botVersion='DRAFT',
                    localeId=locale_id,
                    intentName=intent['intentName'],
                    description=intent.get('description', ''),
                    sampleUtterances=intent.get('sampleUtterances', []),
                    slots=intent.get('slots', []),
                    fulfillmentCodeHook={
                        'enabled': True,
                        'fulfillmentUpdatesSpecification': {
                            'active': False
                        }
                    } if lambda_arn else {'enabled': False}
                )
            
            logger.info(f"Intent {intent_name} operation completed")
    
    def build_bot_locale(self, bot_id: str, locale_id: str) -> None:
        """Build bot locale"""
        logger.info(f"Building bot locale {locale_id}...")
        
        self.lex_client.build_bot_locale(
            botId=bot_id,
            botVersion='DRAFT',
            localeId=locale_id
        )
        
        # Wait for build to complete
        while True:
            response = self.lex_client.describe_bot_locale(
                botId=bot_id,
                botVersion='DRAFT',
                localeId=locale_id
            )
            
            status = response['botLocaleStatus']
            logger.info(f"Build status: {status}")
            
            if status == 'Built':
                logger.info("Bot locale build completed successfully")
                break
            elif status == 'Failed':
                raise Exception(f"Bot locale build failed: {response.get('failureReasons', [])}")
            
            time.sleep(10)
    
    def create_bot_version(self, bot_id: str) -> str:
        """Create bot version"""
        logger.info("Creating bot version...")
        
        response = self.lex_client.create_bot_version(
            botId=bot_id,
            description=f"Version created by deployment script at {time.strftime('%Y-%m-%d %H:%M:%S')}",
            botVersionLocaleSpecification={
                'en_US': {
                    'sourceBotVersion': 'DRAFT'
                }
            }
        )
        
        bot_version = response['botVersion']
        
        # Wait for version to be available
        while True:
            response = self.lex_client.describe_bot_version(
                botId=bot_id,
                botVersion=bot_version
            )
            
            status = response['botStatus']
            logger.info(f"Version status: {status}")
            
            if status == 'Available':
                logger.info(f"Bot version {bot_version} is available")
                break
            elif status == 'Failed':
                raise Exception(f"Bot version creation failed: {response.get('failureReasons', [])}")
            
            time.sleep(10)
        
        return bot_version
    
    def setup_lambda_permissions(self, lambda_arn: str, bot_id: str) -> None:
        """Setup Lambda permissions for Lex"""
        try:
            statement_id = f"lex-invoke-{bot_id}"
            
            # Remove existing permission if it exists
            try:
                self.lambda_client.remove_permission(
                    FunctionName=lambda_arn,
                    StatementId=statement_id
                )
            except self.lambda_client.exceptions.ResourceNotFoundException:
                pass
            
            # Add permission
            self.lambda_client.add_permission(
                FunctionName=lambda_arn,
                StatementId=statement_id,
                Action='lambda:InvokeFunction',
                Principal='lexv2.amazonaws.com',
                SourceArn=f"arn:aws:lex:{self.region}:*:bot/{bot_id}"
            )
            
            logger.info(f"Lambda permissions configured for {lambda_arn}")
            
        except Exception as e:
            logger.warning(f"Failed to configure Lambda permissions: {e}")


def main():
    parser = argparse.ArgumentParser(description='Deploy Amazon Lex bot')
    parser.add_argument('--bot-config', required=True, help='Bot configuration JSON file')
    parser.add_argument('--locale-config', required=True, help='Locale configuration JSON file')
    parser.add_argument('--intents-config', required=True, help='Intents configuration JSON file')
    parser.add_argument('--slot-types-config', required=True, help='Slot types configuration JSON file')
    parser.add_argument('--lambda-arn', help='Lambda function ARN for fulfillment')
    parser.add_argument('--environment', default='dev', help='Environment name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    try:
        # Load configurations
        with open(args.bot_config, 'r') as f:
            bot_config = json.load(f)
        
        with open(args.locale_config, 'r') as f:
            locale_config = json.load(f)
        
        with open(args.intents_config, 'r') as f:
            intents_config = json.load(f)
        
        with open(args.slot_types_config, 'r') as f:
            slot_types_config = json.load(f)
        
        # Initialize deployer
        deployer = LexBotDeployer(region=args.region)
        
        # Deploy bot
        logger.info("Starting Lex bot deployment...")
        
        # 1. Create or update bot
        bot_id = deployer.create_or_update_bot(bot_config)
        
        # 2. Create or update locale
        deployer.create_or_update_bot_locale(bot_id, locale_config)
        
        # 3. Create slot types
        deployer.create_slot_types(bot_id, locale_config['localeId'], slot_types_config)
        
        # 4. Create intents
        deployer.create_intents(bot_id, locale_config['localeId'], intents_config, args.lambda_arn)
        
        # 5. Setup Lambda permissions
        if args.lambda_arn:
            deployer.setup_lambda_permissions(args.lambda_arn, bot_id)
        
        # 6. Build bot locale
        deployer.build_bot_locale(bot_id, locale_config['localeId'])
        
        # 7. Create bot version
        bot_version = deployer.create_bot_version(bot_id)
        
        logger.info(f"Lex bot deployment completed successfully!")
        logger.info(f"Bot ID: {bot_id}")
        logger.info(f"Bot Version: {bot_version}")
        
        # Output results
        result = {
            'bot_id': bot_id,
            'bot_version': bot_version,
            'locale_id': locale_config['localeId'],
            'status': 'success'
        }
        
        with open('lex-deployment-result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        
        # Output error result
        result = {
            'status': 'failed',
            'error': str(e)
        }
        
        with open('lex-deployment-result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        exit(1)


if __name__ == '__main__':
    main()

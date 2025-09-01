const AWS = require('aws-sdk');

// Initialize AWS services
const dynamodb = new AWS.DynamoDB.DocumentClient();
const cognito = new AWS.CognitoIdentityServiceProvider();

exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event, null, 2));
    
    const headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    };

    // Handle CORS preflight
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ message: 'CORS preflight successful' })
        };
    }

    try {
        const path = event.path || event.resource;
        const method = event.httpMethod;
        
        // Route to appropriate handler
        if (path.includes('/profile') && method === 'GET') {
            return await getUserProfile(event, headers);
        } else if (path.includes('/profile') && method === 'PUT') {
            return await updateUserProfile(event, headers);
        } else if (path.includes('/preferences') && method === 'GET') {
            return await getUserPreferences(event, headers);
        } else if (path.includes('/preferences') && method === 'PUT') {
            return await updateUserPreferences(event, headers);
        } else {
            return {
                statusCode: 404,
                headers,
                body: JSON.stringify({ error: 'Endpoint not found' })
            };
        }

    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                error: 'Internal server error',
                message: error.message
            })
        };
    }
};

async function getUserProfile(event, headers) {
    try {
        // Get user ID from JWT token (handled by API Gateway authorizer)
        const userId = event.requestContext.authorizer?.claims?.sub;
        
        if (!userId) {
            return {
                statusCode: 401,
                headers,
                body: JSON.stringify({ error: 'Unauthorized' })
            };
        }

        // Get user profile from DynamoDB
        const params = {
            TableName: process.env.USERS_TABLE || 'ai-assistant-users',
            Key: { user_id: userId }
        };

        const result = await dynamodb.get(params).promise();
        
        if (!result.Item) {
            // Create default profile if doesn't exist
            const defaultProfile = {
                user_id: userId,
                email: event.requestContext.authorizer?.claims?.email,
                username: event.requestContext.authorizer?.claims?.['cognito:username'],
                created_at: new Date().toISOString(),
                preferences: {
                    voice_enabled: true,
                    tts_enabled: true,
                    theme: 'dark'
                }
            };

            await dynamodb.put({
                TableName: process.env.USERS_TABLE || 'ai-assistant-users',
                Item: defaultProfile
            }).promise();

            return {
                statusCode: 200,
                headers,
                body: JSON.stringify(defaultProfile)
            };
        }

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(result.Item)
        };

    } catch (error) {
        console.error('Error getting user profile:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ error: 'Failed to get user profile' })
        };
    }
}

async function updateUserProfile(event, headers) {
    try {
        const userId = event.requestContext.authorizer?.claims?.sub;
        
        if (!userId) {
            return {
                statusCode: 401,
                headers,
                body: JSON.stringify({ error: 'Unauthorized' })
            };
        }

        const body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
        
        // Update user profile
        const params = {
            TableName: process.env.USERS_TABLE || 'ai-assistant-users',
            Key: { user_id: userId },
            UpdateExpression: 'SET #username = :username, #updated_at = :updated_at',
            ExpressionAttributeNames: {
                '#username': 'username',
                '#updated_at': 'updated_at'
            },
            ExpressionAttributeValues: {
                ':username': body.username,
                ':updated_at': new Date().toISOString()
            },
            ReturnValues: 'ALL_NEW'
        };

        const result = await dynamodb.update(params).promise();

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(result.Attributes)
        };

    } catch (error) {
        console.error('Error updating user profile:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ error: 'Failed to update user profile' })
        };
    }
}

async function getUserPreferences(event, headers) {
    try {
        const userId = event.requestContext.authorizer?.claims?.sub;
        
        if (!userId) {
            return {
                statusCode: 401,
                headers,
                body: JSON.stringify({ error: 'Unauthorized' })
            };
        }

        const params = {
            TableName: process.env.USERS_TABLE || 'ai-assistant-users',
            Key: { user_id: userId },
            ProjectionExpression: 'preferences'
        };

        const result = await dynamodb.get(params).promise();
        
        const preferences = result.Item?.preferences || {
            voice_enabled: true,
            tts_enabled: true,
            theme: 'dark'
        };

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(preferences)
        };

    } catch (error) {
        console.error('Error getting user preferences:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ error: 'Failed to get user preferences' })
        };
    }
}

async function updateUserPreferences(event, headers) {
    try {
        const userId = event.requestContext.authorizer?.claims?.sub;
        
        if (!userId) {
            return {
                statusCode: 401,
                headers,
                body: JSON.stringify({ error: 'Unauthorized' })
            };
        }

        const body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
        
        const params = {
            TableName: process.env.USERS_TABLE || 'ai-assistant-users',
            Key: { user_id: userId },
            UpdateExpression: 'SET preferences = :preferences, #updated_at = :updated_at',
            ExpressionAttributeNames: {
                '#updated_at': 'updated_at'
            },
            ExpressionAttributeValues: {
                ':preferences': body,
                ':updated_at': new Date().toISOString()
            },
            ReturnValues: 'ALL_NEW'
        };

        const result = await dynamodb.update(params).promise();

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(result.Attributes.preferences)
        };

    } catch (error) {
        console.error('Error updating user preferences:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ error: 'Failed to update user preferences' })
        };
    }
}

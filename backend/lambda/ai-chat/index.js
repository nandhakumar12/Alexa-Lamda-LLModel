const AWS = require('aws-sdk');

// Initialize AWS services
const dynamodb = new AWS.DynamoDB.DocumentClient();

// Claude AI integration (using AWS Bedrock)
const bedrock = new AWS.BedrockRuntime({
    region: process.env.AWS_REGION || 'us-east-1'
});

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
        // Parse request body
        const body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
        const { message, user_id, conversation_id } = body;

        if (!message) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ error: 'Message is required' })
            };
        }

        // Store user message in DynamoDB
        await storeMessage(conversation_id, user_id, message, 'user');

        // Get AI response
        const aiResponse = await getAIResponse(message, user_id);

        // Store AI response in DynamoDB
        await storeMessage(conversation_id, user_id, aiResponse, 'assistant');

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                response: aiResponse,
                conversation_id,
                timestamp: new Date().toISOString()
            })
        };

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

async function getAIResponse(message, userId) {
    try {
        // Use AWS Bedrock with Claude
        const prompt = `Human: ${message}\n\nAssistant: I'm Nandhakumar's AI Assistant. `;
        
        const params = {
            modelId: 'anthropic.claude-3-haiku-20240307-v1:0',
            contentType: 'application/json',
            accept: 'application/json',
            body: JSON.stringify({
                anthropic_version: "bedrock-2023-05-31",
                max_tokens: 1000,
                messages: [
                    {
                        role: "user",
                        content: message
                    }
                ],
                system: "You are Nandhakumar's AI Assistant, a helpful and friendly AI built with AWS services. You can help with questions, have conversations, and provide assistance. Always be polite and helpful."
            })
        };

        const response = await bedrock.invokeModel(params).promise();
        const responseBody = JSON.parse(response.body.toString());
        
        return responseBody.content[0].text;
        
    } catch (error) {
        console.error('AI Error:', error);
        
        // Fallback responses if Bedrock is not available
        const fallbackResponses = {
            greeting: "Hello! I'm Nandhakumar's AI Assistant. How can I help you today?",
            help: "I can help you with various tasks, answer questions, and have conversations. What would you like to know?",
            time: `The current time is ${new Date().toLocaleTimeString()}.`,
            date: `Today's date is ${new Date().toLocaleDateString()}.`,
            default: "I understand you're asking about something. While I'm having some technical difficulties with my advanced AI features, I'm still here to help! Could you try rephrasing your question?"
        };

        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
            return fallbackResponses.greeting;
        } else if (lowerMessage.includes('help') || lowerMessage.includes('what can you do')) {
            return fallbackResponses.help;
        } else if (lowerMessage.includes('time')) {
            return fallbackResponses.time;
        } else if (lowerMessage.includes('date')) {
            return fallbackResponses.date;
        } else if (lowerMessage.includes('nandhakumar')) {
            return "Nandhakumar is the creator of this AI assistant! He built this using modern AWS services and AI technology to provide you with an intelligent conversational experience.";
        } else {
            return fallbackResponses.default;
        }
    }
}

async function storeMessage(conversationId, userId, message, role) {
    try {
        const params = {
            TableName: process.env.CONVERSATIONS_TABLE || 'ai-assistant-conversations',
            Item: {
                conversation_id: conversationId,
                message_id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                user_id: userId,
                message: message,
                role: role,
                timestamp: new Date().toISOString(),
                ttl: Math.floor(Date.now() / 1000) + (30 * 24 * 60 * 60) // 30 days TTL
            }
        };

        await dynamodb.put(params).promise();
        console.log('Message stored successfully');
    } catch (error) {
        console.error('Error storing message:', error);
        // Don't throw error, just log it
    }
}

// Get conversation history
async function getConversationHistory(conversationId, limit = 10) {
    try {
        const params = {
            TableName: process.env.CONVERSATIONS_TABLE || 'ai-assistant-conversations',
            KeyConditionExpression: 'conversation_id = :cid',
            ExpressionAttributeValues: {
                ':cid': conversationId
            },
            ScanIndexForward: false,
            Limit: limit
        };

        const result = await dynamodb.query(params).promise();
        return result.Items.reverse(); // Return in chronological order
    } catch (error) {
        console.error('Error getting conversation history:', error);
        return [];
    }
}

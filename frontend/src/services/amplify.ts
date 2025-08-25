import { Amplify } from 'aws-amplify';

export const configureAmplify = () => {
  const config = {
    Auth: {
      region: process.env.REACT_APP_AWS_REGION || 'us-east-1',
      userPoolId: process.env.REACT_APP_COGNITO_USER_POOL_ID || '',
      userPoolWebClientId: process.env.REACT_APP_COGNITO_CLIENT_ID || '',
      identityPoolId: process.env.REACT_APP_COGNITO_IDENTITY_POOL_ID || '',
      mandatorySignIn: true,
    },
    API: {
      endpoints: [
        {
          name: 'voice-assistant-api',
          endpoint: process.env.REACT_APP_API_GATEWAY_URL || '',
          region: process.env.REACT_APP_AWS_REGION || 'us-east-1',
        },
      ],
    },
    Storage: {
      AWSS3: {
        bucket: process.env.REACT_APP_S3_BUCKET || '',
        region: process.env.REACT_APP_AWS_REGION || 'us-east-1',
      },
    },
  };

  try {
    Amplify.configure(config);
    console.log('Amplify configured successfully');
  } catch (error) {
    console.error('Error configuring Amplify:', error);
  }
};

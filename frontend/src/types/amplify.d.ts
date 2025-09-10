// Type declarations for AWS Amplify
declare module 'aws-amplify' {
  export const Auth: any;
  export const Hub: any;
  export const Amplify: any;
}

declare module '@aws-amplify/auth' {
  export interface CognitoUser {
    getUsername(): string;
  }
}

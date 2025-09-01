import React from 'react';
import { useNavigate } from 'react-router-dom';

const ProjectPage: React.FC = () => {
  const navigate = useNavigate();

  const awsServices = [
    {
      name: 'AWS Cognito',
      icon: '🔐',
      description: 'User authentication and authorization with secure sign-up/sign-in flows',
      features: ['Multi-factor authentication', 'Social login integration', 'User pool management']
    },
    {
      name: 'AWS Lambda',
      icon: '⚡',
      description: 'Serverless compute for AI processing and API endpoints',
      features: ['Auto-scaling', 'Pay-per-request', 'Event-driven architecture']
    },
    {
      name: 'Amazon API Gateway',
      icon: '🌐',
      description: 'RESTful APIs for seamless frontend-backend communication',
      features: ['Rate limiting', 'CORS support', 'Request/response transformation']
    },
    {
      name: 'AWS CloudFront',
      icon: '🚀',
      description: 'Global content delivery network for fast, secure content delivery',
      features: ['Edge locations', 'SSL/TLS encryption', 'DDoS protection']
    },
    {
      name: 'Amazon S3',
      icon: '📦',
      description: 'Scalable object storage for static assets and data',
      features: ['99.999999999% durability', 'Versioning', 'Lifecycle policies']
    },
    {
      name: 'AWS Amplify',
      icon: '🔧',
      description: 'Full-stack development platform for rapid deployment',
      features: ['CI/CD pipelines', 'Hosting', 'Backend integration']
    }
  ];

  const techStack = [
    { name: 'React 18', icon: '⚛️', description: 'Modern frontend framework with hooks' },
    { name: 'TypeScript', icon: '📘', description: 'Type-safe JavaScript development' },
    { name: 'Claude Haiku', icon: '🧠', description: 'Advanced AI language model' },
    { name: 'Web Speech API', icon: '🎤', description: 'Browser-native voice recognition' },
    { name: 'AWS SDK', icon: '☁️', description: 'Cloud services integration' },
    { name: 'React Router', icon: '🛣️', description: 'Client-side routing' }
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a0b2e 0%, #16213e 50%, #0f3460 100%)',
      color: '#ffffff',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background Particles */}
      {[...Array(20)].map((_, i) => (
        <div
          key={`particle-${i}`}
          style={{
            position: 'absolute',
            width: `${Math.random() * 4 + 2}px`,
            height: `${Math.random() * 4 + 2}px`,
            borderRadius: '50%',
            background: `rgba(168, 85, 247, ${Math.random() * 0.5 + 0.2})`,
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            animation: `float ${Math.random() * 20 + 10}s linear infinite`,
            animationDelay: `${Math.random() * 20}s`
          }}
        />
      ))}

      {/* Navigation */}
      <nav style={{
        position: 'fixed',
        top: '20px',
        left: '20px',
        right: '20px',
        zIndex: 10,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <button
          onClick={() => navigate('/')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            background: 'rgba(26, 11, 46, 0.8)',
            padding: '12px 20px',
            borderRadius: '20px',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            backdropFilter: 'blur(20px)',
            color: 'white',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
        >
          <span>← Back to Home</span>
        </button>

        <button
          onClick={() => navigate('/auth')}
          style={{
            background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
            border: 'none',
            borderRadius: '15px',
            padding: '12px 24px',
            color: 'white',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
        >
          Try Assistant
        </button>
      </nav>

      {/* Main Content */}
      <div style={{
        padding: '100px 20px 40px',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* Header */}
        <div style={{
          textAlign: 'center',
          marginBottom: '60px'
        }}>
          <h1 style={{
            fontSize: '48px',
            fontWeight: '700',
            background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: '0 0 20px 0'
          }}>
            How This Project Was Built
          </h1>
          <p style={{
            fontSize: '20px',
            color: 'rgba(255,255,255,0.8)',
            maxWidth: '600px',
            margin: '0 auto',
            lineHeight: '1.6'
          }}>
            A comprehensive overview of the architecture, technologies, and AWS services 
            powering Nandhakumar's AI Assistant
          </p>
        </div>

        {/* Architecture Overview */}
        <div style={{
          background: 'rgba(26, 11, 46, 0.6)',
          borderRadius: '20px',
          padding: '40px',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          backdropFilter: 'blur(20px)',
          marginBottom: '40px'
        }}>
          <h2 style={{
            fontSize: '32px',
            fontWeight: '600',
            color: 'white',
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            🏗️ Architecture Overview
          </h2>
          <p style={{
            fontSize: '16px',
            color: 'rgba(255,255,255,0.8)',
            lineHeight: '1.6',
            textAlign: 'center',
            maxWidth: '800px',
            margin: '0 auto'
          }}>
            This AI Assistant is built using a modern serverless architecture on AWS, 
            combining React frontend with cloud-native backend services. The application 
            leverages AWS Cognito for authentication, Lambda functions for AI processing, 
            and CloudFront for global content delivery.
          </p>
        </div>

        {/* AWS Services */}
        <div style={{ marginBottom: '60px' }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: '600',
            color: 'white',
            marginBottom: '40px',
            textAlign: 'center'
          }}>
            ☁️ AWS Services Used
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '20px'
          }}>
            {awsServices.map((service, index) => (
              <div
                key={service.name}
                style={{
                  background: 'rgba(26, 11, 46, 0.6)',
                  borderRadius: '15px',
                  padding: '30px',
                  border: '1px solid rgba(168, 85, 247, 0.3)',
                  backdropFilter: 'blur(20px)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 15px 40px rgba(168, 85, 247, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{
                  fontSize: '40px',
                  marginBottom: '15px'
                }}>
                  {service.icon}
                </div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: 'white',
                  marginBottom: '10px'
                }}>
                  {service.name}
                </h3>
                <p style={{
                  fontSize: '14px',
                  color: 'rgba(255,255,255,0.8)',
                  marginBottom: '15px',
                  lineHeight: '1.5'
                }}>
                  {service.description}
                </p>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0
                }}>
                  {service.features.map((feature, idx) => (
                    <li
                      key={idx}
                      style={{
                        fontSize: '12px',
                        color: 'rgba(255,255,255,0.7)',
                        marginBottom: '5px',
                        paddingLeft: '15px',
                        position: 'relative'
                      }}
                    >
                      <span style={{
                        position: 'absolute',
                        left: 0,
                        color: '#a855f7'
                      }}>
                        ✓
                      </span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div style={{ marginBottom: '60px' }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: '600',
            color: 'white',
            marginBottom: '40px',
            textAlign: 'center'
          }}>
            🛠️ Technology Stack
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '20px'
          }}>
            {techStack.map((tech, index) => (
              <div
                key={tech.name}
                style={{
                  background: 'rgba(26, 11, 46, 0.6)',
                  borderRadius: '15px',
                  padding: '25px',
                  border: '1px solid rgba(168, 85, 247, 0.3)',
                  backdropFilter: 'blur(20px)',
                  textAlign: 'center',
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{
                  fontSize: '30px',
                  marginBottom: '10px'
                }}>
                  {tech.icon}
                </div>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: 'white',
                  marginBottom: '8px'
                }}>
                  {tech.name}
                </h3>
                <p style={{
                  fontSize: '14px',
                  color: 'rgba(255,255,255,0.7)',
                  margin: 0,
                  lineHeight: '1.4'
                }}>
                  {tech.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Call to Action */}
        <div style={{
          textAlign: 'center',
          background: 'rgba(26, 11, 46, 0.6)',
          borderRadius: '20px',
          padding: '40px',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          backdropFilter: 'blur(20px)'
        }}>
          <h2 style={{
            fontSize: '32px',
            fontWeight: '600',
            color: 'white',
            marginBottom: '20px'
          }}>
            Ready to Experience the AI Assistant?
          </h2>
          <p style={{
            fontSize: '16px',
            color: 'rgba(255,255,255,0.8)',
            marginBottom: '30px',
            maxWidth: '500px',
            margin: '0 auto 30px'
          }}>
            Sign up now and start chatting with Nandhakumar's AI Assistant powered by 
            cutting-edge AWS infrastructure and Claude AI.
          </p>
          <button
            onClick={() => navigate('/auth')}
            style={{
              background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '25px',
              padding: '18px 36px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 10px 30px rgba(168, 85, 247, 0.4)'
            }}
          >
            🚀 Get Started Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProjectPage;

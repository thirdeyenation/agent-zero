import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, Carousel, ProgressBar, Badge } from 'shadcn';
import { CursorArrowRaysIcon, UserGroupIcon, RocketLaunchIcon, SparklesIcon } from '@heroicons/react/24/outline';

const Dashboard = () => {
  const [content, setContent] = useState([]);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Simulate fetching content from an API
    const fetchContent = async () => {
      const response = await fetch('/api/content');
      const data = await response.json();
      setContent(data);
    };

    fetchContent();
  }, []);

  useEffect(() => {
    // Simulate progress update
    const interval = setInterval(() => {
      setProgress((prevProgress) => (prevProgress >= 100 ? 0 : prevProgress + 10));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="fixed w-full bg-white/80 backdrop-blur-sm z-50 shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">The Agency System</h1>
          <nav className="hidden md:flex space-x-6">
            <a href="#features" className="text-gray-600 hover:text-blue-600">Features</a>
            <a href="#benefits" className="text-gray-600 hover:text-blue-600">Benefits</a>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              Get Started
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="container mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Revolutionize Your Content Experience
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Leverage advanced AI to transform how you consume and create online content.
              Personalized experiences meet streamlined workflows.
            </p>
            <div className="flex justify-center gap-4">
              <button className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg hover:bg-blue-700">
                Start Free Trial
              </button>
              <button className="border border-blue-600 text-blue-600 px-8 py-4 rounded-lg text-lg hover:bg-blue-50">
                Learn More
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16">Core Features</h2>
          <div className="grid md:grid-cols-2 gap-12">
            {/* Curator Agent */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-white p-8 rounded-2xl shadow-lg"
            >
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
                <CursorArrowRaysIcon className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Curator Agent</h3>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <SparklesIcon className="w-6 h-6 text-blue-600 mr-2 flex-shrink-0" />
                  <span>Personalized content curation through AI-powered recommendations</span>
                </li>
                <li className="flex items-start">
                  <SparklesIcon className="w-6 h-6 text-blue-600 mr-2 flex-shrink-0" />
                  <span>Multi-platform content aggregation from various sources</span>
                </li>
                <li className="flex items-start">
                  <SparklesIcon className="w-6 h-6 text-blue-600 mr-2 flex-shrink-0" />
                  <span>Customized viewing experiences and themed playlists</span>
                </li>
              </ul>
            </motion.div>

            {/* Manager Agent */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-white p-8 rounded-2xl shadow-lg"
            >
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
                <UserGroupIcon className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Manager Agent</h3>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <SparklesIcon className="w-6 h-6 text-blue-600 mr-2 flex-shrink-0" />
                  <span>Complete podcast production workflow automation</span>
                </li>
                <li className="flex items-start">
                  <SparklesIcon className="w-6 h-6 text-blue-600 mr-2 flex-shrink-0" />
                  <span>Intelligent marketing and audience growth strategies</span>
                </li>
                <li className="flex items-start">
                  <SparklesIcon className="w-6 h-6 text-blue-600 mr-2 flex-shrink-0" />
                  <span>Automated administrative task management</span>
                </li>
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="benefits" className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16">Key Benefits</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <CursorArrowRaysIcon className="w-6 h-6" />,
                title: "Personalized Experience",
                description: "Enjoy content tailored to your interests and preferences"
              },
              {
                icon: <RocketLaunchIcon className="w-6 h-6" />,
                title: "Streamlined Workflow",
                description: "Focus on creation while AI handles the technical details"
              },
              {
                icon: <SparklesIcon className="w-6 h-6" />,
                title: "Enhanced Discovery",
                description: "Discover new content that matches your interests"
              }
            ].map((benefit, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center p-6"
              >
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <div className="text-blue-600">{benefit.icon}</div>
                </div>
                <h3 className="text-xl font-bold mb-2">{benefit.title}</h3>
                <p className="text-gray-600">{benefit.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">

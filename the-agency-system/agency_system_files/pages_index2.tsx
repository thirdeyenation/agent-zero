import { useState, useEffect } from 'react';
import { Card, Carousel, ProgressBar, Badge } from 'shadcn';

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
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-blue-100 p-8">
      <h1 className="text-3xl font-bold text-blue-900 mb-8">Welcome to Your Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {content.map((item, index) => (
          <Card key={index} className="p-4 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow">
            <h2 className="text-xl font-semibold text-blue-800">{item.title}</h2>
            <p className="text-gray-600 mt-2">{item.description}</p>
          </Card>
        ))}
      </div>
      <div className="mt-8">
        <h2 className="text-2xl font-bold text-blue-900 mb-4">Your Progress</h2>
        <ProgressBar value={progress} className="h-2 bg-blue-200 rounded-full" />
        <Badge className="mt-2 bg-blue-500 text-white">{progress}% Complete</Badge>
      </div>
      <div className="mt-8">
        <h2 className="text-2xl font-bold text-blue-900 mb-4">Featured Content</h2>
        <Carousel>
          {content.slice(0, 5).map((item, index) => (
            <div key={index} className="p-4 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow">
              <h3 className="text-lg font-semibold text-blue-800">{item.title}</h3>
              <p className="text-gray-600 mt-2">{item.description}</p>
            </div>
          ))}
        </Carousel>
      </div>
    </div>
  );
};

export default Dashboard;
import React, { useState, useRef } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Search, Loader2, ThumbsUp, ThumbsDown, Share2, Bookmark } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const [problemStatement, setProblemStatement] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [feedback, setFeedback] = useState({});
  const [sessionId] = useState(() => uuidv4());
  const { toast } = useToast();

  const handleSearch = async () => {
    if (!problemStatement.trim()) {
      toast({
        title: "Please describe your problem",
        description: "Enter a detailed description of what you need help with.",
        variant: "destructive"
      });
      return;
    }

    setIsSearching(true);
    
    try {
      const response = await axios.post(`${API}/recommend`, {
        problem_statement: problemStatement,
        excluded_solutions: [],
        user_preferences: {}
      });
      
      setRecommendations(response.data);
      setFeedback({});
      
      toast({
        title: "Recommendations Generated!",
        description: `Found ${response.data.length} AI solutions for your needs.`,
      });
      
    } catch (error) {
      console.error('Error getting recommendations:', error);
      toast({
        title: "Error",
        description: "Failed to generate recommendations. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleFeedback = async (solutionName, type, rank) => {
    try {
      await axios.post(`${API}/feedback`, {
        session_id: sessionId,
        solution_name: solutionName,
        feedback_type: type,
        recommendation_rank: rank,
        problem_statement: problemStatement
      });
      
      setFeedback(prev => ({ ...prev, [`${solutionName}-${rank}`]: type }));
      
      toast({
        title: "Thank you for your feedback!",
        description: "Your input helps us improve our recommendations.",
      });
    } catch (error) {
      console.error('Error submitting feedback:', error);
      toast({
        title: "Error",
        description: "Failed to submit feedback.",
        variant: "destructive"
      });
    }
  };

  const handleSave = async (solutionName) => {
    try {
      await axios.post(`${API}/save-solution`, {
        session_id: sessionId,
        solution_name: solutionName,
        problem_statement: problemStatement
      });
      
      toast({
        title: "Solution saved!",
        description: "You can find it in your saved solutions.",
      });
    } catch (error) {
      console.error('Error saving solution:', error);
      toast({
        title: "Error",
        description: "Failed to save solution.",
        variant: "destructive"
      });
    }
  };

  const handleShare = () => {
    const shareText = `Check out these AI solutions I found: ${recommendations.map(r => r.name).join(', ')}`;
    navigator.clipboard.writeText(`${shareText}\n\n${window.location.href}`);
    toast({
      title: "Link copied!",
      description: "Share these recommendations with others.",
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-600 bg-clip-text text-transparent">
            Find Your Perfect AI Solution
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Describe your problem in natural language, and our AI will recommend the best solution for your specific needs.
          </p>
        </div>
      </div>

      {/* Search Section */}
      <Card className="shadow-lg border-0 bg-white/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5 text-blue-500" />
            <span>Describe Your Problem</span>
          </CardTitle>
          <CardDescription>
            Be as specific as possible about what you need help with
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Example: I need to create professional marketing videos for my business, but I don't have video editing skills or expensive software..."
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
            className="min-h-32 resize-none"
          />
          <Button 
            onClick={handleSearch}
            disabled={isSearching}
            className="w-full bg-gradient-to-r from-blue-500 to-emerald-500 hover:from-blue-600 hover:to-emerald-600 text-white font-medium py-6"
          >
            {isSearching ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Finding Your AI Solution...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Find My AI Solution
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results Section */}
      {recommendations.length > 0 && (
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-slate-800 mb-2">
              Top {recommendations.length} Recommended Solutions
            </h2>
            <p className="text-slate-600">
              Based on your requirements, here are the best AI solutions for you
            </p>
          </div>
          
          <div className="space-y-6">
            {recommendations.map((recommendation, index) => (
              <Card key={index} className="shadow-xl border-0 bg-white">
                <CardHeader className="bg-gradient-to-r from-blue-50 to-emerald-50">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-blue-500 to-emerald-500 text-white rounded-full text-sm font-bold">
                          {recommendation.rank}
                        </div>
                        <CardTitle className="text-xl text-slate-800">
                          {recommendation.name}
                        </CardTitle>
                      </div>
                      <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                        {recommendation.category}
                      </Badge>
                    </div>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline" onClick={() => handleSave(recommendation.name)}>
                        <Bookmark className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline" onClick={handleShare}>
                        <Share2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-6 space-y-4">
                  <div>
                    <p className="text-slate-600 leading-relaxed">
                      {recommendation.description}
                    </p>
                  </div>

                  <div className="bg-slate-50 rounded-lg p-4">
                    <h4 className="font-medium text-slate-800 mb-2">Why This Solution?</h4>
                    <p className="text-slate-600 text-sm">
                      {recommendation.explanation}
                    </p>
                  </div>

                  <div>
                    <h4 className="font-medium text-slate-800 mb-2">Perfect For:</h4>
                    <div className="flex flex-wrap gap-2">
                      {recommendation.use_cases.map((useCase, caseIndex) => (
                        <Badge key={caseIndex} variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">
                          {useCase}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-slate-600">Was this helpful?</span>
                        <div className="flex space-x-2">
                          <Button
                            size="sm"
                            variant={feedback === `up-${index}` ? 'default' : 'outline'}
                            onClick={() => handleFeedback(`up-${index}`)}
                            className="h-8"
                          >
                            <ThumbsUp className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant={feedback === `down-${index}` ? 'default' : 'outline'}
                            onClick={() => handleFeedback(`down-${index}`)}
                            className="h-8"
                          >
                            <ThumbsDown className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      <Button asChild className="bg-gradient-to-r from-blue-500 to-emerald-500 hover:from-blue-600 hover:to-emerald-600">
                        <a href={recommendation.link} target="_blank" rel="noopener noreferrer">
                          Try {recommendation.name}
                        </a>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Search, ExternalLink, Filter } from 'lucide-react';
import { aiSolutions } from '../data/mockData';

const SolutionLibrary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  // Get unique categories
  const categories = useMemo(() => {
    const cats = [...new Set(aiSolutions.map(solution => solution.category))];
    return ['all', ...cats];
  }, []);

  // Filter solutions
  const filteredSolutions = useMemo(() => {
    return aiSolutions.filter(solution => {
      const matchesSearch = searchTerm === '' || 
                           solution.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           solution.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           solution.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           solution.use_cases.some(useCase => 
                             useCase.toLowerCase().includes(searchTerm.toLowerCase())
                           );
      
      const matchesCategory = selectedCategory === 'all' || solution.category === selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }, [searchTerm, selectedCategory]);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent">
          AI Solutions Library
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Browse our comprehensive collection of AI tools and solutions for every use case.
        </p>
      </div>

      {/* Filters */}
      <Card className="shadow-lg border-0 bg-white/50 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search solutions, categories, or use cases..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="md:w-64">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Filter by category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.slice(1).map(category => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Count */}
      <div className="text-slate-600">
        Showing {filteredSolutions.length} of {aiSolutions.length} solutions
        {selectedCategory !== 'all' && ` in ${selectedCategory}`}
      </div>

      {/* Solutions Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredSolutions.map((solution, index) => (
          <Card key={index} className="shadow-lg border-0 bg-white hover:shadow-xl transition-all duration-300 group">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="text-lg group-hover:text-blue-600 transition-colors">
                    {solution.name}
                  </CardTitle>
                  <Badge variant="secondary" className="bg-blue-50 text-blue-700 text-xs">
                    {solution.category}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <CardDescription className="text-slate-600 leading-relaxed">
                {solution.description}
              </CardDescription>
              
              <div>
                <h4 className="text-sm font-medium text-slate-800 mb-2">Use Cases:</h4>
                <div className="flex flex-wrap gap-1">
                  {solution.use_cases.map((useCase, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs bg-emerald-50 text-emerald-700 border-emerald-200">
                      {useCase}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="pt-2">
                <Button 
                  asChild 
                  className="w-full bg-gradient-to-r from-blue-500 to-emerald-500 hover:from-blue-600 hover:to-emerald-600 text-white"
                >
                  <a href={solution.link} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Visit {solution.name}
                  </a>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* No Results */}
      {filteredSolutions.length === 0 && (
        <Card className="shadow-lg border-0 bg-white/50 backdrop-blur-sm">
          <CardContent className="p-12 text-center">
            <div className="space-y-4">
              <Search className="h-12 w-12 text-slate-300 mx-auto" />
              <h3 className="text-lg font-medium text-slate-600">No solutions found</h3>
              <p className="text-slate-500">
                Try adjusting your search terms or filter criteria.
              </p>
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchTerm('');
                  setSelectedCategory('all');
                }}
              >
                Clear Filters
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SolutionLibrary;
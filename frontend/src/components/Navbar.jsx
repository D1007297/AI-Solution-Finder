import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from './ui/button';
import { Search, Library, Sparkles } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-lg group-hover:scale-105 transition-transform">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent">
              AI Solution Finder
            </span>
          </Link>
          
          <div className="flex items-center space-x-4">
            <Link to="/">
              <Button 
                variant={location.pathname === "/" ? "default" : "ghost"}
                className="flex items-center space-x-2"
              >
                <Search className="h-4 w-4" />
                <span>Find Solution</span>
              </Button>
            </Link>
            <Link to="/library">
              <Button 
                variant={location.pathname === "/library" ? "default" : "ghost"}
                className="flex items-center space-x-2"
              >
                <Library className="h-4 w-4" />
                <span>Browse Library</span>
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
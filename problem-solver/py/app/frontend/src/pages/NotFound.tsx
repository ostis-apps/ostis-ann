
import React, { useEffect } from "react";
import { useLocation, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Home, ArrowLeft } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center neural-gradient-bg p-6">
      <div className="text-center max-w-md">
        <div className="relative mb-6 inline-block">
          <div className="h-24 w-24 rounded-full bg-neural-primary/20 flex items-center justify-center mx-auto animate-pulse-soft">
            <span className="text-5xl font-bold text-neural-primary">404</span>
          </div>
          <div className="absolute -top-2 -right-2 h-8 w-8 rounded-full bg-neural-accent flex items-center justify-center animate-float">
            <span className="text-xl font-bold text-white">?</span>
          </div>
        </div>
        <h1 className="text-3xl font-bold mb-4 text-foreground">Страница не найдена</h1>
        <p className="text-lg text-muted-foreground mb-8">
          Запрошенный ресурс не существует или был перемещен.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button asChild className="flex items-center gap-2">
            <Link to="/">
              <Home className="h-5 w-5" />
              <span>На главную</span>
            </Link>
          </Button>
          <Button variant="outline" onClick={() => window.history.back()} className="flex items-center gap-2">
            <ArrowLeft className="h-5 w-5" />
            <span>Назад</span>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;


import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { cn } from '@/library/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  description,
  icon,
  trend,
  className
}) => {
  return (
    <Card className={cn(className)}>
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
            <h3 className="text-2xl font-bold">{value}</h3>
            {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
            
            {trend && (
              <div className="flex items-center mt-2">
                <div 
                  className={cn(
                    "text-xs flex items-center",
                    trend.isPositive ? "text-neural-success" : "text-neural-error"
                  )}
                >
                  {trend.isPositive ? (
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M8 4L12 8L8 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M4 8H12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M8 12L4 8L8 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M4 8H12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  )}
                  <span className="ml-1">{Math.abs(trend.value)}%</span>
                  <span className="ml-1 text-muted-foreground">с прошлой недели</span>
                </div>
              </div>
            )}
          </div>
          
          {icon && (
            <div className="rounded-lg p-2 bg-muted">
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default StatCard;

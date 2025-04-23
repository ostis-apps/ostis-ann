
import React from 'react';
import { Sidebar, SidebarContent, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Menu, Moon, Sun, BrainCircuit } from "lucide-react";
import AppSidebar from './AppSidebar';
import ThemeToggle from './ThemeToggle';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <AppSidebar />
        <div className="flex flex-col flex-1">
          <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
            <div className="flex h-14 items-center px-4 md:px-6 justify-between">
              <div className="flex items-center gap-2">
                <SidebarTrigger>
                  <Button variant="ghost" size="icon" aria-label="Toggle sidebar">
                    <Menu className="h-5 w-5" />
                    <span className="sr-only">Toggle sidebar</span>
                  </Button>
                </SidebarTrigger>
                <div className="flex items-center gap-2">
                  <BrainCircuit className="h-6 w-6 text-neural-accent" />
                  <span className="font-semibold text-lg hidden md:inline-block">Нейро Мастер</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <ThemeToggle />
              </div>
            </div>
          </header>
          <main className="flex-1">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
};

export default MainLayout;

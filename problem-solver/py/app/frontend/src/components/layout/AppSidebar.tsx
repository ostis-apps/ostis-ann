
import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Sidebar, 
  SidebarContent, 
  SidebarFooter, 
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton
} from '@/components/ui/sidebar';

import { 
  BarChartBig, 
  Brain, 
  BookOpen, 
  LayoutDashboard,
  FolderKanban,
  MessageSquareText,
  Settings,
  HelpCircle,
  Layers
} from 'lucide-react';

const AppSidebar: React.FC = () => {
  return (
    <Sidebar className="border-r">
      <SidebarHeader className="flex items-center gap-2 px-6 py-3">
        <Brain className="h-6 w-6 text-neural-accent" />
        <span className="font-semibold">Нейро Мастер</span>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Основное</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/" className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                      isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 
                      'hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                    }`
                  }>
                    <LayoutDashboard className="h-5 w-5" />
                    <span>Панель управления</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/create" className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                      isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 
                      'hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                    }`
                  }>
                    <Brain className="h-5 w-5" />
                    <span>Конструктор ИНС</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/models" className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                      isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 
                      'hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                    }`
                  }>
                    <Layers className="h-5 w-5" />
                    <span>Библиотека моделей</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/projects" className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                      isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 
                      'hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                    }`
                  }>
                    <FolderKanban className="h-5 w-5" />
                    <span>Проекты</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/compare" className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                      isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 
                      'hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                    }`
                  }>
                    <BarChartBig className="h-5 w-5" />
                    <span>Сравнение моделей</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Помощь</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/assistant" className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                      isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 
                      'hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                    }`
                  }>
                    <MessageSquareText className="h-5 w-5" />
                    <span>ИИ-ассистент</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/docs" className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                      isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 
                      'hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                    }`
                  }>
                    <BookOpen className="h-5 w-5" />
                    <span>Документация</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <div className="px-3 py-2">
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton asChild>
                <NavLink to="/settings" className={({ isActive }) => 
                  `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                    isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 
                    'hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                  }`
                }>
                  <Settings className="h-5 w-5" />
                  <span>Настройки</span>
                </NavLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton asChild>
                <NavLink to="/help" className={({ isActive }) => 
                  `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                    isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 
                    'hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                  }`
                }>
                  <HelpCircle className="h-5 w-5" />
                  <span>Справка</span>
                </NavLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
};

export default AppSidebar;

# Dashboard Design and Folder Structure

## **Dashboard Design Plan**

### **1. Sidebar Design**

- **Features:**

  - Logo and App Name
  - Navigation links:
    - Dashboard Overview
    - Workflows
    - Integrations
    - AI Tasks
    - Webhooks
    - Analytics
    - Team Management
    - API Keys
    - Settings
  - “Create Workflow/Task” button below the navigation links.

- **Style:**

  - Color: Background – Dark gray (#1E1E2C), Text – Light gray (#F5F5F5)
  - Hover Effect: Highlight selected/hovered menu item with an accent color (e.g., #5A9BD5).
  - Icons alongside menu items for better navigation.

### **2. Individual Page Designs**

#### **Dashboard Overview Page**

- **Key Features:**
  - **Statistics Cards:** Total workflows, tasks, integrations, API usage.
  - **Recent Activity Feed:** Logs for workflows and tasks.
  - **Performance Graphs:** Trends for task completion and API usage.
  - **Quick Actions:** Buttons to create workflows, manage integrations, or access settings.

#### **Workflows Page**

- **Key Features:**
  - List of workflows with status indicators (Active/Paused).
  - Search and filter workflows by tags, date, or status.
  - Quick Preview Panel: Details and logs for selected workflows.
  - Action Buttons: Edit, duplicate, or delete workflows.

#### **Integrations Page**

- **Key Features:**
  - **Integration Marketplace:** Grid of available integrations with search and filter.
  - **Connected Integrations:** List of active integrations with statuses.
  - **Actions:** Connect, disconnect, or manage integrations.

#### **AI Tasks Page**

- **Key Features:**
  - Task queue overview with statuses (Queued, In-progress, Completed).
  - Task details with input data, AI results, and error logs.
  - Filters for task type, status, and date.
  - Action Buttons: Retry or cancel tasks.

#### **Webhooks Page**

- **Key Features:**
  - List of webhooks with statuses.
  - Add Webhook Form: Configure URL, events, and security.
  - Logs Panel: Recent webhook activity.

#### **Analytics Page**

- **Key Features:**
  - Performance charts for task execution, API calls, and team activity.
  - Customizable dashboard with widgets for specific analytics.
  - Downloadable reports in CSV or PDF.

#### **Team Management Page**

- **Key Features:**
  - List of team members with roles and statuses.
  - Invite new members with role assignments.
  - Activity logs for team actions.

#### **API Keys Page**

- **Key Features:**
  - Table of API keys with scopes and usage stats.
  - Create New Key Form: Specify scopes and expiration.
  - Action Buttons: Revoke or regenerate keys.

#### **Settings Page**

- **Key Features:**
  - General settings: Profile, notifications, and passwords.
  - App customization: Themes and language preferences.
  - Security: Manage 2FA, login alerts, and session expirations.

---

## **Folder Structure for Dashboard Implementation**

### **Overview**

The folder structure is modular and scalable, adhering to best practices for component-based architecture. Each page and component is isolated for ease of development, testing, and maintenance.

### **Proposed Folder Structure**

```plaintext
app/
├── layout.tsx            # Layout for the dashboard
├── page.tsx              # Main dashboard page
├── dashboard-overview/   # Dashboard Overview page
│   ├── page.tsx          # Entry point for the page
│   ├── DashboardStats.tsx
│   ├── RecentActivity.tsx
│   └── PerformanceGraphs.tsx
├── workflows/            # Workflows page
│   ├── page.tsx
│   ├── WorkflowList.tsx
│   ├── WorkflowPreview.tsx
│   └── WorkflowFilters.tsx
├── integrations/         # Integrations page
│   ├── page.tsx
│   ├── IntegrationMarketplace.tsx
│   └── ConnectedIntegrations.tsx
├── ai-tasks/             # AI Tasks page
│   ├── page.tsx
│   ├── TaskQueue.tsx
│   ├── TaskDetails.tsx
│   └── TaskFilters.tsx
├── webhooks/             # Webhooks page
│   ├── page.tsx
│   ├── WebhookList.tsx
│   ├── AddWebhookForm.tsx
│   └── WebhookLogs.tsx
├── analytics/            # Analytics page
│   ├── page.tsx
│   ├── PerformanceCharts.tsx
│   └── AnalyticsWidgets.tsx
├── team-management/      # Team Management page
│   ├── page.tsx
│   ├── TeamList.tsx
│   ├── InviteMembersForm.tsx
│   └── ActivityLogs.tsx
├── api-keys/             # API Keys page
│   ├── page.tsx
│   ├── APIKeyList.tsx
│   ├── CreateAPIKeyForm.tsx
│   └── KeyManagement.tsx
├── settings/             # Settings page
│   ├── page.tsx
│   ├── GeneralSettings.tsx
│   ├── SecuritySettings.tsx
│   └── AppCustomization.tsx

components/               # Reusable UI components
├── Button/
├── Card/
├── Modal/
├── Sidebar/
├── Navbar/
├── InputField/
├── Table/
├── Graph/

styles/                   # Global and component-specific styles
├── globals.css
├── variables.css
└── components/

utils/                    # Utility functions and helpers
├── apiClient.ts
├── authHelpers.ts
├── dateFormatter.ts
├── errorHandler.ts
└── validators.ts

contexts/                 # Context providers for global state
├── AuthContext.tsx
├── ThemeContext.tsx
├── WorkflowContext.tsx
└── SidebarContext.tsx

hooks/                    # Custom React hooks
├── useFetch.ts
├── useSidebar.ts
├── useAuth.ts
└── useAnalytics.ts
```

### **Key Points in Structure**

1. **App Router Compatibility:**
   - Each feature or page is a separate folder under `app/` with its own `page.tsx` for routing.
2. **Modular Components:**
   - All UI elements are in `components/`, ensuring reusability across pages.
3. **Page Isolation:**
   - Each page has its own folder, keeping logic, components, and styles localized.
4. **Global State Management:**
   - Contexts for authentication, theming, workflows, and sidebar.
5. **Custom Hooks:**
   - Hooks encapsulate reusable logic like API fetching and state management.
6. **Scalability:**
   - Easily extendable for future features like advanced analytics or real-time updates.

Would you like a prototype for any specific page or component to get started?


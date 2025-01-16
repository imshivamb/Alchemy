export interface TeamUser {
    id: string;
    email: string;
    name: string;
    is_active: boolean;
  }

  export interface TeamMember {
    id: string;
    user: TeamUser;
    role: string;
    joined_at: string;
    created_at: string;
    updated_at: string;
  }
  

  export interface RoleDistribution {
    role: string;
    count: number;
  }

  export interface TeamStatistics {
    total_members: number;
    active_members: number;
    roles_distribution: RoleDistribution[];
  }
  
  export interface TeamDetail {
    id: string;
    name: string;
    description: string;
    owner_email: string;
    members_count: number;
    created_at: string;
    updated_at: string;
    members: TeamMember[];
    statistics: TeamStatistics;
  }
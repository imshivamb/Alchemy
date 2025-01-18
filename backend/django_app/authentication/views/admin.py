from datetime import datetime, timedelta
from django.db.models import Count, Q, Avg
from ..serializers import (
    UserExportSerializer,
    DetailedTeamSerializer,
    UserPlanUpdateSerializer
)
from ..models import UserProfile, SecurityLog ,TeamActivity, TeamMembership, Team
from .base import BaseViewSet
from rest_framework.response import Response
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import get_user_model
from ..models import Workspace, UserActivity
from ..serializers import UserActivitySerializer,TeamAuditLogSerializer, SecurityLogSerializer, DetailedWorkspaceSerializer 

User = get_user_model()

class AdminUserViewSet(BaseViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = UserExportSerializer
    @swagger_auto_schema(
        operation_summary="List all users",
        operation_description="Get a list of all users with optional filters",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search in email, name, and organization",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'is_active', openapi.IN_QUERY,
                description="Filter by active status",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'plan_type', openapi.IN_QUERY,
                description="Filter by plan type",
                type=openapi.TYPE_STRING,
                enum=['free', 'basic', 'premium', 'enterprise']
            ),
        ],
        responses={
            200: UserExportSerializer(many=True),
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Users']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve user details",
        operation_description="Get detailed information about a specific user",
        responses={
            200: UserExportSerializer,
            404: 'User not found',
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Users']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update user",
        operation_description="Update user information and settings",
        request_body=UserExportSerializer,
        responses={
            200: UserExportSerializer,
            400: 'Invalid data',
            403: 'Forbidden - Admin access required',
            404: 'User not found'
        },
        tags=['Admin - Users']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Bulk user operations",
        operation_description="Perform operations on multiple users",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['operation', 'user_ids'],
            properties={
                'operation': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['activate', 'deactivate', 'delete', 'update_plan']
                ),
                'user_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                ),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Additional data for the operation'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Operation completed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'processed': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'failed': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'errors': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
            400: 'Invalid operation or data',
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Users']
    )
    @action(detail=False, methods=['post'])
    def bulk(self, request):
        pass

    @swagger_auto_schema(
        operation_summary="User statistics",
        operation_description="Get detailed statistics about user activity and usage",
        responses={
            200: openapi.Response(
                description="User statistics retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'active_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'plan_distribution': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            )
                        ),
                        'signup_trend': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'date': openapi.Schema(type=openapi.TYPE_STRING),
                                    'count': openapi.Schema(type=openapi.TYPE_INTEGER)
                                }
                            )
                        )
                    }
                )
            ),
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Users']
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        pass

    @swagger_auto_schema(
        operation_summary="Update user plan",
        operation_description="Update a user's subscription plan",
        request_body=UserPlanUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Plan updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'old_plan': openapi.Schema(type=openapi.TYPE_STRING),
                        'new_plan': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: 'Invalid plan type',
            403: 'Forbidden - Admin access required',
            404: 'User not found'
        },
        tags=['Admin - Users']
    )
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Apply filters
        filters = {}
        
        if self.request.query_params.get('is_active'):
            filters['is_active'] = self.request.query_params['is_active'] == 'true'
            
        if self.request.query_params.get('plan_type'):
            filters['profile__plan_type'] = self.request.query_params['plan_type']
            
        if self.request.query_params.get('joined_after'):
            filters['date_joined__gte'] = self.request.query_params['joined_after']
            
        # Apply search
        search = self.request.query_params.get('search')
        if search:
            return queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(organization__icontains=search)
            ).filter(**filters)
            
        return queryset.filter(**filters)

    @action(detail=True, methods=['post'])
    def update_plan(self, request, pk=None):
        user = self.get_object()
        serializer = UserPlanUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            old_plan = user.profile.plan_type
            new_plan = serializer.validated_data['plan_type']
            
            user.profile.plan_type = new_plan
            user.profile.save()
            
            # Log plan change
            SecurityLog.objects.create(
                user=user,
                action='plan_updated',
                details={
                    'old_plan': old_plan,
                    'new_plan': new_plan,
                    'updated_by': request.user.id
                }
            )
            
            return Response({
                'message': 'Plan updated successfully',
                'user_id': str(user.id),
                'old_plan': old_plan,
                'new_plan': new_plan
            })
            
        return Response(serializer.errors, status=400)

class AdminTeamViewSet(BaseViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = DetailedTeamSerializer
    @swagger_auto_schema(
        operation_summary="List all teams",
        operation_description="Get a list of all teams with filtering options",
        manual_parameters=[
            openapi.Parameter(
                'workspace_id', openapi.IN_QUERY,
                description="Filter by workspace",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'owner_id', openapi.IN_QUERY,
                description="Filter by team owner",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'created_after', openapi.IN_QUERY,
                description="Filter by creation date",
                type=openapi.TYPE_STRING,
                format='date'
            ),
            openapi.Parameter(
                'member_count', openapi.IN_QUERY,
                description="Filter by minimum member count",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: DetailedTeamSerializer(many=True),
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Teams']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Transfer team ownership",
        operation_description="Transfer ownership of a team to another user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['new_owner_id'],
            properties={
                'new_owner_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='UUID of the new owner'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Ownership transferred successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous_owner': openapi.Schema(type=openapi.TYPE_STRING),
                        'new_owner': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: 'Invalid request',
            403: 'Forbidden - Admin access required',
            404: 'Team not found'
        },
        tags=['Admin - Teams']
    )
    def get_queryset(self):
        queryset = Team.objects.all()
        
        # Apply filters
        if self.request.query_params.get('owner_id'):
            queryset = queryset.filter(
                owner_id=self.request.query_params['owner_id']
            )
            
        if self.request.query_params.get('created_after'):
            queryset = queryset.filter(
                created_at__gte=self.request.query_params['created_after']
            )
            
        return queryset
    
    @swagger_auto_schema(
        operation_summary="Transfer team ownership",
        operation_description="Transfer ownership of a team to another user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['new_owner_id'],
            properties={
                'new_owner_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User ID of the new owner'
                ),
                'notify_members': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Whether to notify team members'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Ownership transferred successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'team_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous_owner': openapi.Schema(type=openapi.TYPE_STRING),
                        'new_owner': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: 'Invalid request',
            403: 'Forbidden - Admin access required',
            404: 'Team or user not found'
        },
        tags=['Admin - Teams']
    )

    @action(detail=True, methods=['post'])
    def transfer_ownership(self, request, pk=None):
        team = self.get_object()
        new_owner_id = request.data.get('new_owner_id')
        
        try:
            new_owner = User.objects.get(id=new_owner_id)
            old_owner = team.owner
            
            team.owner = new_owner
            team.save()
            
            # Update memberships
            TeamMembership.objects.filter(
                team=team,
                user=new_owner
            ).update(role='admin')
            
            # Log ownership transfer
            TeamAuditLog.objects.create(
                team=team,
                user=request.user,
                action='ownership_transferred',
                changes={
                    'old_owner': str(old_owner.id),
                    'new_owner': str(new_owner.id)
                }
            )
            
            return Response({
                'message': 'Ownership transferred successfully',
                'previous_owner': str(old_owner.id),
                'new_owner': str(new_owner.id)
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'New owner not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    @swagger_auto_schema(
        operation_summary="Team audit logs",
        operation_description="Get audit logs for a specific team",
        manual_parameters=[
            openapi.Parameter(
                'start_date', openapi.IN_QUERY,
                description="Filter by start date",
                type=openapi.TYPE_STRING,
                format='date'
            ),
            openapi.Parameter(
                'end_date', openapi.IN_QUERY,
                description="Filter by end date",
                type=openapi.TYPE_STRING,
                format='date'
            )
        ],
        responses={
            200: TeamAuditLogSerializer(many=True),
            403: 'Forbidden - Admin access required',
            404: 'Team not found'
        },
        tags=['Admin - Teams']
    )
    @action(detail=True, methods=['get'])
    def audit_logs(self, request, pk=None):
        pass
            
class AdminWorkspaceViewSet(BaseViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = DetailedWorkspaceSerializer

    @swagger_auto_schema(
        operation_summary="List all workspaces",
        operation_description="Admin access to all workspaces with filters",
        manual_parameters=[
            openapi.Parameter(
                'owner_id', openapi.IN_QUERY,
                description="Filter by workspace owner",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'plan_type', openapi.IN_QUERY,
                description="Filter by plan type",
                type=openapi.TYPE_STRING,
                enum=['free', 'business', 'enterprise']
            ),
        ],
        tags=['Admin - Workspaces']
    )
    def get_queryset(self):
        queryset = Workspace.objects.all()
        
        # Apply filters
        if self.request.query_params.get('owner_id'):
            queryset = queryset.filter(owner_id=self.request.query_params['owner_id'])
            
        if self.request.query_params.get('plan_type'):
            queryset = queryset.filter(plan_type=self.request.query_params['plan_type'])
            
        return queryset.select_related('owner')

    @action(detail=True, methods=['post'])
    def update_plan(self, request, pk=None):
        workspace = self.get_object()
        new_plan = request.data.get('plan_type')
        old_plan = workspace.plan_type
        
        workspace.plan_type = new_plan
        workspace.save()
        
        SecurityLog.objects.create(
            user=request.user,
            action='workspace_plan_updated',
            severity='medium',
            details={
                'workspace_id': str(workspace.id),
                'old_plan': old_plan,
                'new_plan': new_plan
            }
        )
        
        return Response({'message': 'Plan updated successfully'})
    
class AdminAnalyticsViewSet(BaseViewSet):
    permission_classes = [IsAdminUser]
    @swagger_auto_schema(
        operation_summary="System overview metrics",
        operation_description="Get system-wide analytics overview",
        manual_parameters=[
            openapi.Parameter(
                'time_range', openapi.IN_QUERY,
                description="Time range for metrics",
                type=openapi.TYPE_STRING,
                enum=['24h', '7d', '30d', '90d']
            )
        ],
        responses={
            200: openapi.Response(
                description="Analytics overview retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'users': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'active': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'new': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'workspaces': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'by_plan': openapi.Schema(type=openapi.TYPE_OBJECT)
                            }
                        ),
                        'teams': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'avg_size': openapi.Schema(type=openapi.TYPE_NUMBER)
                            }
                        )
                    }
                )
            ),
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Analytics']
    )
    @action(detail=False)
    def overview(self, request):
        """System-wide analytics overview"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        stats = {
            'users': {
                'total': User.objects.count(),
                'active': User.objects.filter(is_active=True).count(),
                'new_last_30_days': User.objects.filter(
                    created_at__gte=start_date
                ).count()
            },
            'workspaces': {
                'total': Workspace.objects.count(),
                'by_plan': dict(Workspace.objects.values_list(
                    'plan_type'
                ).annotate(count=Count('id')))
            },
            'teams': {
                'total': Team.objects.count(),
                'average_size': TeamMembership.objects.values(
                    'team'
                ).annotate(size=Count('id')).aggregate(avg=Avg('size'))['avg']
            },
            'security': {
                'critical_logs': SecurityLog.objects.filter(
                    severity='critical',
                    created_at__gte=start_date
                ).count()
            }
        }
        return Response(stats)
    
    @swagger_auto_schema(
        operation_summary="User analytics",
        operation_description="Get detailed user-related analytics",
        manual_parameters=[
            openapi.Parameter(
                'start_date', openapi.IN_QUERY,
                description="Start date for analytics",
                type=openapi.TYPE_STRING,
                format='date'
            ),
            openapi.Parameter(
                'end_date', openapi.IN_QUERY,
                description="End date for analytics",
                type=openapi.TYPE_STRING,
                format='date'
            )
        ],
        responses={
            200: openapi.Response(
                description="User analytics retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'growth': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'date': openapi.Schema(type=openapi.TYPE_STRING),
                                    'total_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'new_users': openapi.Schema(type=openapi.TYPE_INTEGER)
                                }
                            )
                        ),
                        'retention': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'daily': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'weekly': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'monthly': openapi.Schema(type=openapi.TYPE_NUMBER)
                            }
                        )
                    }
                )
            ),
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Analytics']
    )

    @action(detail=False)
    def user_metrics(self, request):
        """Detailed user-related metrics"""
        time_periods = [7, 30, 90]
        metrics = {}
        
        for days in time_periods:
            date_threshold = timezone.now() - timedelta(days=days)
            metrics[f'last_{days}_days'] = {
                'new_users': User.objects.filter(
                    created_at__gte=date_threshold
                ).count(),
                'active_users': UserActivity.objects.filter(
                    created_at__gte=date_threshold
                ).values('user').distinct().count(),
                'upgrades': UserActivity.objects.filter(
                    action='plan_upgraded',
                    created_at__gte=date_threshold
                ).count()
            }
            
        return Response(metrics)
    
class AdminSystemViewSet(BaseViewSet):
    permission_classes = [IsAdminUser]
    @swagger_auto_schema(
        operation_summary="System health check",
        operation_description="Get system health metrics and status",
        responses={
            200: openapi.Response(
                description="System health status retrieved",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=['healthy', 'degraded', 'down']
                        ),
                        'database': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'status': openapi.Schema(type=openapi.TYPE_STRING),
                                'latency': openapi.Schema(type=openapi.TYPE_NUMBER)
                            }
                        ),
                        'memory_usage': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'storage': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'used': openapi.Schema(type=openapi.TYPE_NUMBER)
                            }
                        ),
                        'last_check': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - System']
    )
    @action(detail=False)
    def health(self, request):
        """System health check"""
        # Basic system metrics
        metrics = {
            'database': self._check_database_health(),
            'security': {
                'critical_alerts': SecurityLog.objects.filter(
                    severity='critical',
                    is_resolved=False
                ).count()
            },
            'activity': {
                'last_24h_actions': UserActivity.objects.filter(
                    created_at__gte=timezone.now() - timedelta(hours=24)
                ).count()
            }
        }
        return Response(metrics)

    @action(detail=False)
    def security_logs(self, request):
        """Security log access"""
        logs = SecurityLog.objects.all().order_by('-created_at')[:100]
        return Response(SecurityLogSerializer(logs, many=True).data)

    def _check_database_health(self):
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "error", "details": str(e)}
        
        
class AdminActivityViewSet(BaseViewSet):
    permission_classes = [IsAdminUser]
    
    @action(detail=False)
    def user_activity(self, request):
        activities = UserActivity.objects.all().select_related(
            'user'
        ).order_by('-created_at')
        
        return Response(UserActivitySerializer(activities, many=True).data)

    @action(detail=False)
    def security_alerts(self, request):
        alerts = SecurityLog.objects.filter(
            severity__in=['high', 'critical'],
            is_resolved=False
        ).order_by('-created_at')
        
        return Response(SecurityLogSerializer(alerts, many=True).data)

    @action(detail=False)
    def export_logs(self, request):
        """Export activity logs"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        query = UserActivity.objects.all()
        if start_date:
            query = query.filter(created_at__gte=start_date)
        if end_date:
            query = query.filter(created_at__lte=end_date)
            
        activities = query.select_related('user').order_by('-created_at')
        serializer = UserActivitySerializer(activities, many=True)
        
        return Response(serializer.data)
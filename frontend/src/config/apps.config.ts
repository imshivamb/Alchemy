import { 
    Mail, 
    FileSpreadsheet, 
    Calendar, 
    MessageSquare, 
    Webhook, 
    Brain,
    Coins
  } from 'lucide-react';
  
  export type AppType = {
    id: string;
    name: string;
    description: string;
    icon: any;
    category: 'automation' | 'communication' | 'google' | 'blockchain' | 'ai';
    triggers?: {
      id: string;
      name: string;
      description: string;
      configSchema: any; // We'll define this later
    }[];
    actions?: {
      id: string;
      name: string;
      description: string;
      configSchema: any;
    }[];
  };
  
  export const apps: AppType[] = [
    {
      id: 'gmail',
      name: 'Gmail',
      description: 'Trigger on new emails or send emails',
      icon: Mail,
      category: 'google',
      triggers: [
        {
          id: 'new_email',
          name: 'New Email',
          description: 'Triggers when a new email is received',
          configSchema: {} 
        },
        {
          id: 'new_labeled_email',
          name: 'New Labeled Email',
          description: 'Triggers when an email with specific label is received',
          configSchema: {}
        }
      ],
      actions: [
        {
          id: 'send_email',
          name: 'Send Email',
          description: 'Send an email through Gmail',
          configSchema: {}
        },
        {
          id: 'read_emails',
          name: 'Read Emails',
          description: 'Read emails from Gmail',
          configSchema: {}
        },
        {
          id: 'update_labels',
          name: 'Update Labels',
          description: 'Add or remove Gmail labels',
          configSchema: {}
        }
      ]
    },
    {
      id: 'sheets',
      name: 'Google Sheets',
      description: 'Work with spreadsheet data',
      icon: FileSpreadsheet,
      category: 'google',
      triggers: [
        {
          id: 'new_row',
          name: 'New Row',
          description: 'Triggers when a new row is added',
          configSchema: {}
        }
      ],
      actions: [
        {
          id: 'create_spreadsheet',
          name: 'Create Spreadsheet',
          description: 'Create a new Google Spreadsheet',
          configSchema: {}
        },
        {
          id: 'append_row',
          name: 'Append Row',
          description: 'Add a new row to a spreadsheet',
          configSchema: {}
        },
        {
          id: 'update_values',
          name: 'Update Values',
          description: 'Update values in a spreadsheet',
          configSchema: {}
        },
        {
          id: 'clear_values',
          name: 'Clear Values',
          description: 'Clear values from a range',
          configSchema: {}
        }
      ]
    },
    {
      id: 'calendar',
      name: 'Google Calendar',
      description: 'Manage calendar events and schedules',
      icon: Calendar,
      category: 'google',
      triggers: [
        {
          id: 'new_event',
          name: 'New Event',
          description: 'Triggers when a new event is created',
          configSchema: {}
        },
        {
          id: 'event_updated',
          name: 'Event Updated',
          description: 'Triggers when an event is modified',
          configSchema: {}
        }
      ],
      actions: [
        {
          id: 'create_event',
          name: 'Create Event',
          description: 'Create a new calendar event',
          configSchema: {}
        },
        {
          id: 'update_event',
          name: 'Update Event',
          description: 'Update an existing event',
          configSchema: {}
        },
        {
          id: 'delete_event',
          name: 'Delete Event',
          description: 'Delete a calendar event',
          configSchema: {}
        }
      ]
    },
    {
      id: 'slack',
      name: 'Slack',
      description: 'Send messages and interact with Slack',
      icon: MessageSquare,
      category: 'communication',
      triggers: [
        {
          id: 'new_message',
          name: 'New Message',
          description: 'Triggers when a new message is posted',
          configSchema: {}
        }
      ],
      actions: [
        {
          id: 'send_message',
          name: 'Send Message',
          description: 'Send a message to a channel',
          configSchema: {}
        },
        {
          id: 'create_channel',
          name: 'Create Channel',
          description: 'Create a new Slack channel',
          configSchema: {}
        },
        {
          id: 'upload_file',
          name: 'Upload File',
          description: 'Upload a file to Slack',
          configSchema: {}
        },
        {
          id: 'add_reaction',
          name: 'Add Reaction',
          description: 'Add a reaction to a message',
          configSchema: {}
        }
      ]
    },
    {
      id: 'webhook',
      name: 'Webhooks',
      description: 'Send and receive web requests',
      icon: Webhook,
      category: 'automation',
      triggers: [
        {
          id: 'incoming_webhook',
          name: 'Incoming Webhook',
          description: 'Triggers when a webhook is received',
          configSchema: {}
        }
      ],
      actions: [
        {
          id: 'send_webhook',
          name: 'Send Webhook',
          description: 'Send a webhook request',
          configSchema: {}
        }
      ]
    },
    {
      id: 'ai',
      name: 'AI Processing',
      description: 'Process data with AI models',
      icon: Brain,
      category: 'ai',
      actions: [
        {
          id: 'process_text',
          name: 'Process Text',
          description: 'Process text with AI models',
          configSchema: {}
        },
        {
          id: 'batch_process',
          name: 'Batch Process',
          description: 'Process multiple items with AI',
          configSchema: {}
        }
      ]
    },
    {
      id: 'web3',
      name: 'Web3',
      description: 'Blockchain interactions and transfers',
      icon: Coins,
      category: 'blockchain',
      actions: [
        {
          id: 'transfer',
          name: 'Transfer',
          description: 'Transfer tokens or coins',
          configSchema: {}
        },
        {
          id: 'mint',
          name: 'Mint Tokens',
          description: 'Mint new tokens',
          configSchema: {}
        },
        {
          id: 'burn',
          name: 'Burn Tokens',
          description: 'Burn existing tokens',
          configSchema: {}
        },
        {
          id: 'stake',
          name: 'Stake',
          description: 'Stake tokens',
          configSchema: {}
        },
        {
          id: 'unstake',
          name: 'Unstake',
          description: 'Unstake tokens',
          configSchema: {}
        }
      ]
    }
  ];
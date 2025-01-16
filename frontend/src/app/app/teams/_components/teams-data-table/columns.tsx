import { ColumnDef } from "@tanstack/react-table";
import { TeamDetail } from "@/types/teams.types";
import { Button } from "@/components/ui/button";
import { ArrowUpDown } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { TableRowActions } from "./row-actions";

export const columns: ColumnDef<TeamDetail>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={table.getIsAllPageRowsSelected()}
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
  },
  {
    accessorKey: "members_count",
    header: "Members",
    cell: ({ row }) => <div>{row.original.members_count}</div>,
  },
  {
    accessorKey: "owner_email",
    header: "Owner",
  },
  {
    accessorKey: "created_at",
    header: "Created",
    cell: ({ row }) => (
      <div>{new Date(row.original.created_at).toLocaleDateString()}</div>
    ),
  },
  {
    id: "actions",
    cell: ({ row }) => <TableRowActions row={row} />,
  },
];

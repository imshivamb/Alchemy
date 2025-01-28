import { useState } from "react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { formatDistanceToNow } from "date-fns";
import { Web3Task, TransactionStatus } from "@/types/web3.types";
import { useWeb3Store } from "@/stores/web3.store";

interface ExtendedTransaction extends Web3Task {
  signature?: string;
  amount?: string;
  recipient?: string;
}

export function TransactionHistory() {
  const { tasks, selectedNetwork } = useWeb3Store();
  const [searchQuery, setSearchQuery] = useState("");

  // Filter only transfer and token transactions
  const transactions = tasks.filter((task) =>
    ["transfer", "mint", "burn"].includes(task.action_type)
  ) as ExtendedTransaction[];

  const filteredTransactions = transactions.filter(
    (tx) =>
      tx.workflow_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tx.action_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tx.signature?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusColor = (status: TransactionStatus) => {
    const colors = {
      [TransactionStatus.PENDING]: "bg-yellow-100 text-yellow-800",
      [TransactionStatus.PROCESSING]: "bg-blue-100 text-blue-800",
      [TransactionStatus.COMPLETED]: "bg-green-100 text-green-800",
      [TransactionStatus.FAILED]: "bg-red-100 text-red-800",
    };
    return colors[status];
  };

  const formatAmount = (amount?: string | number) => {
    if (!amount) return "-";
    return parseFloat(amount.toString()).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 9,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Transaction History</CardTitle>
        <CardDescription>
          Recent transactions on {selectedNetwork}
        </CardDescription>
        <Input
          placeholder="Search transactions..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-sm mt-4"
        />
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Transaction</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredTransactions.map((tx) => (
              <TableRow key={tx.workflow_id}>
                <TableCell>
                  <div className="font-mono">
                    {tx.signature
                      ? `${tx.signature.slice(0, 8)}...${tx.signature.slice(
                          -8
                        )}`
                      : `${tx.workflow_id.slice(0, 8)}...`}
                  </div>
                  {tx.recipient && (
                    <div className="text-xs text-muted-foreground">
                      To: {tx.recipient.slice(0, 8)}...
                    </div>
                  )}
                </TableCell>
                <TableCell>
                  <span className="capitalize">{tx.action_type}</span>
                  {tx.params?.token_mint && (
                    <div className="text-xs text-muted-foreground">
                      Token: {tx.params.token_mint.slice(0, 8)}...
                    </div>
                  )}
                </TableCell>
                <TableCell>
                  {formatAmount(tx.params?.amount)}
                  <span className="text-xs text-muted-foreground ml-1">
                    {tx.params?.token_mint ? "Tokens" : "SOL"}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge className={getStatusColor(tx.status)}>
                    {tx.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  {formatDistanceToNow(new Date(tx.created_at))} ago
                </TableCell>
              </TableRow>
            ))}
            {filteredTransactions.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="text-center text-muted-foreground"
                >
                  No transactions found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { useWeb3Store } from "@/stores/web3.store";

interface ValidatorListProps {
  onSelectValidator: (validator: string) => void;
}

export function ValidatorList({ onSelectValidator }: ValidatorListProps) {
  const { validators } = useWeb3Store();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredValidators = validators.filter((validator) =>
    validator.pubkey.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Validators</CardTitle>
        <Input
          placeholder="Search validators..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-sm"
        />
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Validator</TableHead>
              <TableHead>Commission (%)</TableHead>
              <TableHead>APY (%)</TableHead>
              <TableHead className="text-right">Total Stake (SOL)</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredValidators.map((validator) => (
              <TableRow key={validator.pubkey}>
                <TableCell className="font-mono">
                  {validator.pubkey.slice(0, 8)}...
                </TableCell>
                <TableCell>{validator.commission}%</TableCell>
                <TableCell>
                  {(
                    (validator.credits * 100) /
                    validator.activated_stake
                  ).toFixed(2)}
                  %
                </TableCell>
                <TableCell className="text-right">
                  {(validator.activated_stake / 1e9).toLocaleString()} SOL
                </TableCell>
                <TableCell>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onSelectValidator(validator.pubkey)}
                  >
                    Select
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

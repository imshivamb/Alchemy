import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
} from "@/components/ui/pagination";

interface WebhookPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function WebhookPagination({
  currentPage,
  totalPages,
  onPageChange,
}: WebhookPaginationProps) {
  return (
    <Pagination>
      <PaginationContent className="space-x-2">
        <PaginationItem>
          <PaginationLink
            onClick={() => currentPage > 1 && onPageChange(currentPage - 1)}
            className={
              currentPage === 1 ? "pointer-events-none opacity-50" : ""
            }
          >
            Previous
          </PaginationLink>
        </PaginationItem>

        {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
          <PaginationItem key={page}>
            <PaginationLink
              isActive={page === currentPage}
              onClick={() => onPageChange(page)}
            >
              {page}
            </PaginationLink>
          </PaginationItem>
        ))}

        <PaginationItem>
          <PaginationLink
            onClick={() =>
              currentPage < totalPages && onPageChange(currentPage + 1)
            }
            className={
              currentPage === totalPages ? "pointer-events-none opacity-50" : ""
            }
          >
            Next
          </PaginationLink>
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}

import * as z from "zod";

export const profileFormSchema = z.object({
    first_name: z.string().min(1, "First name is required").max(150),
    last_name: z.string().min(1, "Last name is required").max(150),
    email: z
      .string()
      .email("Invalid email address")
      .min(1, "Email is required")
      .max(254),
    phone_number: z.string().max(15).nullable(),
    organization: z.string().max(100).nullable(),
    profile: z.object({
      timezone: z.string().min(1, "Timezone is required"),
    }),
  });
  
 export type ProfileFormValues = z.infer<typeof profileFormSchema>;
import * as z from 'zod';


//Login Schema
export const loginSchema = z.object({
    email: z.string().email('Please Enter a valid Email'),
    password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
})


//Register Schema
export const registerSchema = z.object({
    email: z.string().email('Please Enter a valid Email'),
    password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
    confirm_password: z.string(),
    first_name: z.string().min(1, 'Please enter your first name'),
    last_name: z.string().min(1, 'Please enter your last name'),
    organization: z.string().optional(),
    phone_number: z.string().optional(),
}).refine((data) => data.password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
})


//Forget Password Schema
export const forgetPasswordSchema = z.object({
    email: z.string().email('Please Enter a valid Email'),
})

//Reset Password Schema
export const resetPasswordSchema = z.object({
    password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirm_password: z.string()
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
})


export type RegisterFormValues = z.infer<typeof registerSchema>;
export type LoginFormValues = z.infer<typeof loginSchema>;
export type ForgetPasswordValues = z.infer<typeof forgetPasswordSchema>;
export type ResetPasswordValues = z.infer<typeof resetPasswordSchema>;
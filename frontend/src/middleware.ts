import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  // const { pathname } = request.nextUrl;
  const token = request.cookies.get('accessToken')?.value;

  // If accessing auth pages while logged in
  if ( token) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // // If accessing protected pages while logged out
  // if ( !token && !pathname.startsWith('/_next')) {
  //     const url = new URL('/auth/login', request.url);
  //     // Only add callbackUrl if it's not a system path
  //     if (!pathname.startsWith('/api/') && pathname !== '/') {
  //         url.searchParams.set('callbackUrl', pathname);
  //     }
  //     return NextResponse.redirect(url);
  // }

  return NextResponse.next();
}
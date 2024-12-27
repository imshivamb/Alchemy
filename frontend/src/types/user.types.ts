export interface UpdateProfilePictureResponse {
    message: string;
    profile_picture_url: string;
}

export interface UpdateProfileData {
    first_name: string;
    last_name: string;
    email: string;
    phone_number?: string | null;
    organization?: string | null;
    profile: {
      timezone: string;
    };
  }
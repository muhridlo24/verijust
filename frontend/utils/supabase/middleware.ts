
import { createClient as createSupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY;

export const createClient = () => {
  // For middleware, we'll use a simple client without cookie handling
  // Cookie handling should be done in server components if needed
  return createSupabaseClient(
    supabaseUrl!,
    supabaseKey!
  );
};

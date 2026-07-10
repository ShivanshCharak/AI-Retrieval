import {
  createContext,
  useContext,
  useState,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";

type User = {
  name: string;
  email: string;
};

type AuthContextType = {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter()

  function login(user: User) {
    console.log(user)
    setUser(user);
  }

  function logout() {
    console.log("loggin out")
    setUser(null);
    router.push("/login")
  }

  return (
    <AuthContext.Provider
      value={{
        user,

        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}
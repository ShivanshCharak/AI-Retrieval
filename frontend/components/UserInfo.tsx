import { useAuth } from "@/context/AuthContext";
import { Bell, BrickWall, EllipsisVertical, Trash, User } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

type TAuthBlock = {
  sidebarVisibility: boolean;
};

export default function AuthBlock({ sidebarVisibility }: TAuthBlock) {
  const [showAuthOptions, setShowAuthOptions] = useState<boolean>(false);
  const { user, isAuthenticated, logout } = useAuth();
  console.log(user)

  const options = [
    { icon: BrickWall, label: "Billing" },
    { icon: Bell, label: "Notifications" },
    { icon: Trash, label: "Logout", click:logout },
  ];

  function handleClickAuth() {
    setShowAuthOptions((prev) => !prev);
  }

  return (
    <>
      {isAuthenticated ? (
        <div className=" w-[90%] h-[70px] rounded-xl mb-[10px] flex justify-around   bg-gray-100 border-[1px] border-gray-200 hover:bg-gray-100 cursor-pointer">
          <div className="w-[50px] h-[50px] ml-2 my-auto  rounded-full bg-gray-300 ">
            <span className="font-medium flex justify-center h-[50px] w-[50px]  items-center text-gray-500">
              S H
            </span>
            
          </div>
         {sidebarVisibility && <div className=" flex flex-col ml-2 mt-2">
            {user?.email && (
              <span className="text-gray-900 font-semibold ">
               {user.name}
              </span>
            )}
            <span className="text-gray-600 font-semibold"> {user?.email && user?.email.slice(0, 13)}....</span>
          </div>}
          <EllipsisVertical
            className="mt-5"
            width={20}
            onClick={() => handleClickAuth()}
            color="black"
          />
          {showAuthOptions && (
            <>
              <div className="absolute bottom-[70px] right-0 rounded-md px-1 py-4  flex flex-col  w-[150px] border-[1px] border-gray-200 ">
                {options.map((option) => {
                  const Icon = option.icon;
                  return (
                    <span
                      key={option.label}
                      className=" h-[20px] flex justify-start p-5 items-center hover:bg-gray-200 hover:rounded-lg cursor-pointer "
                      onClick={option.click}
                    >
                      <Icon
                        color="gray"
                        size={15}
                        className="mr-2"
                      />
                      <label className="text-gray-500 text-xs font-bold cursor-pointer">{option.label}</label>
                    </span>
                  );
                })}
              </div>
            </>
          )}
        </div>
      ) : (
        <Link href={"/signup"} className="flex justify-center">
          <button className=" w-[90%] text-gray-600 flex items-center  h-[50px] rounded-full mb-[10px]  bg-gray-100 border-[1px] border-gray-200 hover:bg-gray-100 cursor-pointer absolute bottom-3">
            <User className="ml-4" />{" "}
            {sidebarVisibility ? (
              <label htmlFor="" className="flex justify-start">
                Create account
              </label>
            ) : (
              ""
            )}
          </button>
        </Link>
      )}
    </>
  );
}

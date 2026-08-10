import { useCallback, useEffect, useState } from "react";

import { getAccessRoles } from "@/api/auth-api";
import type {
  CreateUserPayload,
  ManagedUser,
  UpdateUserPayload,
} from "@/api/types";
import {
  createUser,
  deleteUser,
  getUsers,
  updateUser,
} from "@/api/user-api";

const fallbackRoles = ["admin", "sales", "manager"];

export function useUserManagement() {
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [roles, setRoles] = useState<string[]>(fallbackRoles);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError("");

    try {
      const [userResponse, roleResponse] = await Promise.all([
        getUsers(),
        getAccessRoles(),
      ]);
      setUsers(userResponse);
      if (roleResponse.roles.length > 0) {
        setRoles(roleResponse.roles);
      }
    } catch (loadError) {
      setError(toErrorMessage(loadError, "Unable to load users."));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function addUser(payload: CreateUserPayload) {
    setError("");

    try {
      const createdUser = await createUser(payload);
      setUsers((current) => [createdUser, ...current]);
      return createdUser;
    } catch (createError) {
      setError(toErrorMessage(createError, "Unable to create user."));
      return null;
    }
  }

  async function editUser(userId: number, payload: UpdateUserPayload) {
    setError("");

    try {
      const updatedUser = await updateUser(userId, payload);
      setUsers((current) =>
        current.map((user) => (user.id === updatedUser.id ? updatedUser : user)),
      );
      return updatedUser;
    } catch (updateError) {
      setError(toErrorMessage(updateError, "Unable to update user."));
      return null;
    }
  }

  async function removeUser(userId: number) {
    setError("");

    try {
      await deleteUser(userId);
      setUsers((current) => current.filter((user) => user.id !== userId));
      return true;
    } catch (deleteError) {
      setError(toErrorMessage(deleteError, "Unable to delete user."));
      return false;
    }
  }

  return {
    users,
    roles,
    isLoading,
    error,
    refresh,
    addUser,
    editUser,
    removeUser,
  };
}

function toErrorMessage(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
}

import { type FormEvent, useMemo, useState } from "react";
import {
  Building2,
  Mail,
  Plus,
  RefreshCw,
  Trash2,
  UserRound,
  Users,
} from "lucide-react";

import {
  AuthFormError,
  AuthInputField,
  PasswordField,
} from "@/components/auth/auth-form";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import type { CreateUserPayload, ManagedUser } from "@/api/types";
import { useUserManagement } from "@/hooks/api";
import { validateEmail, validatePassword } from "@/lib/form-validation";
import { useAuthStore } from "@/store/auth-store";

const protectedAdminEmail = "admin@9to5.com";

export function UserManagementPanel() {
  const currentUser = useAuthStore((state) => state.user);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const {
    users,
    roles,
    isLoading,
    error,
    refresh,
    addUser,
    editUser,
    removeUser,
  } = useUserManagement();

  async function handleUpdate(
    user: ManagedUser,
    payload: { role: string },
  ) {
    await editUser(user.id, payload);
  }

  async function handleDelete(user: ManagedUser) {
    const confirmed = window.confirm(
      `Delete ${user.name}? This action cannot be undone.`,
    );

    if (!confirmed) return;

    await removeUser(user.id);
  }

  return (
    <div className="rounded-lg border bg-white">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-4">
        <div className="flex items-center gap-2">
          <Users className="h-5 w-5 text-primary" />
          <div>
            <h1 className="text-lg font-semibold">User Management</h1>
            <p className="text-sm text-muted-foreground">
              Create users and control their access.
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="gap-2"
            onClick={() => void refresh()}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button
            type="button"
            size="sm"
            className="gap-2"
            onClick={() => setShowCreateForm((current) => !current)}
          >
            <Plus className="h-4 w-4" />
            {showCreateForm ? "Close form" : "Add User"}
          </Button>
        </div>
      </div>

      {showCreateForm ? (
        <CreateUserForm
          roles={roles}
          onCreate={addUser}
          onCreated={() => {
            setShowCreateForm(false);
          }}
          onCancel={() => setShowCreateForm(false)}
        />
      ) : null}

      {error ? (
        <div className="mx-5 mt-5 rounded-md border border-destructive/25 bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive">
          {error}
        </div>
      ) : null}

      <div className="overflow-x-auto p-5">
        {isLoading ? (
          <div className="py-12 text-center text-sm text-muted-foreground">
            Loading users...
          </div>
        ) : users.length === 0 ? (
          <div className="py-12 text-center text-sm text-muted-foreground">
            No users found.
          </div>
        ) : (
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b text-xs uppercase tracking-wide text-muted-foreground">
                <th className="px-3 py-3 font-semibold">User</th>
                <th className="px-3 py-3 font-semibold">Department</th>
                <th className="px-3 py-3 font-semibold">Role</th>
                <th className="px-3 py-3 text-right font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => {
                const isCurrentUser = user.id === currentUser?.id;
                const isProtectedAdmin =
                  user.email.trim().toLowerCase() === protectedAdminEmail;

                return (
                  <tr className="border-b last:border-0" key={user.id}>
                    <td className="px-3 py-4">
                      <p className="font-semibold">
                        {user.name}
                        {isCurrentUser ? (
                          <span className="ml-2 rounded bg-muted px-1.5 py-0.5 text-xs font-medium">
                            You
                          </span>
                        ) : null}
                        {isProtectedAdmin ? (
                          <span className="ml-2 rounded bg-primary/10 px-1.5 py-0.5 text-xs font-medium text-primary">
                            Protected
                          </span>
                        ) : null}
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">{user.email}</p>
                    </td>
                    <td className="px-3 py-4 text-muted-foreground">
                      {user.department || "—"}
                    </td>
                    <td className="px-3 py-4">
                      <select
                        value={user.role}
                        onChange={(event) =>
                          void handleUpdate(user, { role: event.target.value })
                        }
                        disabled={isCurrentUser || isProtectedAdmin}
                        className="h-9 rounded-md border bg-background px-2 text-sm disabled:cursor-not-allowed disabled:opacity-60"
                        aria-label={`Role for ${user.name}`}
                      >
                        {roles.map((role) => (
                          <option key={role} value={role}>
                            {formatRole(role)}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-3 py-4 text-right">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        className="gap-2 text-destructive hover:text-destructive"
                        disabled={isCurrentUser || isProtectedAdmin}
                        onClick={() => void handleDelete(user)}
                        title={
                          isProtectedAdmin
                            ? "The protected administrator cannot be deleted"
                            : undefined
                        }
                      >
                        <Trash2 className="h-4 w-4" />
                        Delete
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function CreateUserForm({
  onCancel,
  onCreate,
  onCreated,
  roles,
}: {
  onCancel: () => void;
  onCreate: (payload: CreateUserPayload) => Promise<ManagedUser | null>;
  onCreated: () => void;
  roles: string[];
}) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [department, setDepartment] = useState("");
  const [role, setRole] = useState("sales");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canSubmit = useMemo(
    () =>
      name.trim().length >= 2 &&
      email.trim().length > 0 &&
      password.length >= 6 &&
      role.length > 0 &&
      !isSubmitting,
    [email, isSubmitting, name, password, role],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    const emailError = validateEmail(email);
    const passwordError = validatePassword(password);

    if (name.trim().length < 2) {
      setError("Full name must be at least 2 characters.");
      return;
    }
    if (emailError || passwordError) {
      setError(emailError ?? passwordError ?? "Check the form values.");
      return;
    }

    setIsSubmitting(true);

    const user = await onCreate({
      name: name.trim(),
      email: email.trim(),
      password,
      role,
      ...(department.trim() ? { department: department.trim() } : {}),
    });

    if (user) {
      onCreated();
    }

    setIsSubmitting(false);
  }

  return (
    <form
      className="grid gap-4 border-b bg-muted/30 p-5 md:grid-cols-2"
      onSubmit={handleSubmit}
      noValidate
    >
      <AuthInputField
        id="new-user-name"
        label="Full name"
        icon={UserRound}
        value={name}
        onChange={(event) => setName(event.target.value)}
        placeholder="Full name"
        autoComplete="off"
      />
      <AuthInputField
        id="new-user-email"
        label="Email"
        icon={Mail}
        type="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        placeholder="user@company.com"
        autoComplete="off"
      />
      <AuthInputField
        id="new-user-department"
        label="Department (optional)"
        icon={Building2}
        value={department}
        onChange={(event) => setDepartment(event.target.value)}
        placeholder="Sales"
        autoComplete="off"
      />
      <div className="space-y-2">
        <Label htmlFor="new-user-role">Role</Label>
        <select
          id="new-user-role"
          value={role}
          onChange={(event) => setRole(event.target.value)}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {roles.map((accessRole) => (
            <option key={accessRole} value={accessRole}>
              {formatRole(accessRole)}
            </option>
          ))}
        </select>
      </div>
      <div className="md:col-span-2">
        <PasswordField
          id="new-user-password"
          label="Temporary password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Minimum 6 characters"
          autoComplete="new-password"
        />
      </div>

      <div className="md:col-span-2">
        <AuthFormError message={error} />
      </div>

      <div className="flex justify-end gap-2 md:col-span-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={!canSubmit}>
          {isSubmitting ? "Creating..." : "Create User"}
        </Button>
      </div>
    </form>
  );
}

function formatRole(role: string) {
  if (role === "sales") return "Salesperson";
  return role.charAt(0).toUpperCase() + role.slice(1);
}

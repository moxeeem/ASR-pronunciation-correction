<script setup lang="ts">
const user = useSupabaseUser();
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const errorMsg = ref('');

const { auth } = useSupabaseClient();
const userRegister = async () => {
    if (password.value !== confirmPassword.value) {
        errorMsg.value = 'Passwords do not match!';
        password.value = '';
        confirmPassword.value = '';
        setTimeout(() => {
            errorMsg.value = '';
        }, 3000);
        return;
    }

    try {
        const { error } = await auth.signUp({
            email: email.value,
            password: password.value,
        });
        email.value = '';
        password.value = '';
        confirmPassword.value = '';

        if (error) throw error;
    } catch (error) {
        errorMsg.value = error.message;
        setTimeout(() => {
            errorMsg.value = '';
        }, 3000);
    }
};

watchEffect(() => {
    if (user.value) {
        return navigateTo('/tasks');
    }
});
</script>

<template>
    <main>
        <section class="container mx-auto flex flex-wrap items-center justify-center px-5 py-24 text-gray-400">
            <form @submit.prevent="userRegister"
                class="bg-opacity-50 mt-10 flex w-full flex-col rounded-lg bg-[#242424] p-8 md:mt-0 md:w-1/2 lg:w-2/6">
                <h2 class="mb-5 text-lg font-medium text-[#aac8e4]">Register</h2>

                <div class="relative mb-4">
                    <label for="email" class="text-sm leading-7 text-gray-400">Email</label>
                    <input v-model="email" type="email" id="email" name="email"
                        class="bg-opacity-20 w-full rounded border border-gray-600 bg-transparent py-1 px-3 text-base leading-8 text-gray-100 outline-none transition-colors duration-200 ease-in-out focus:border-[#42d392] focus:bg-transparent focus:ring-2 focus:ring-transparent"
                        required />
                </div>
                <div class="relative mb-4">
                    <label for="password" class="text-sm leading-7 text-gray-400">Password</label>
                    <input v-model="password" type="password" id="password" name="password"
                        class="bg-opacity-20 w-full rounded border border-gray-600 bg-transparent py-1 px-3 text-base leading-8 text-gray-100 outline-none transition-colors duration-200 ease-in-out focus:border-[#42d392] focus:bg-transparent focus:ring-2 focus:ring-transparent"
                        required />
                </div>
                <div class="relative mb-4">
                    <label for="confirmPassword" class="text-sm leading-7 text-gray-400">Confirm password</label>
                    <input v-model="confirmPassword" type="password" id="confirmPassword" name="confirmPassword"
                        class="bg-opacity-20 w-full rounded border border-gray-600 bg-transparent py-1 px-3 text-base leading-8 text-gray-100 outline-none transition-colors duration-200 ease-in-out focus:border-[#42d392] focus:bg-transparent focus:ring-2 focus:ring-transparent"
                        required />
                </div>
                <button type="submit"
                    class="rounded border-0 bg-[#42b883] py-2 px-8 font-sans font-bold text-[#213547] transition-colors duration-500 hover:bg-[#42d392] focus:outline-none">
                    Submit
                </button>
                <span class="bg-opacity-50 absolute right-8 top-8 rounded-lg bg-[#242424] p-8 px-4 py-2 text-red-500"
                    v-if="errorMsg">{{ errorMsg }}</span>
                <p class="mt-3 text-xs">Do you have an account yet?</p>
                <nuxt-link class="w-fit text-sm text-[#aac8e4] hover:text-[#42b883]" to="/login">Login</nuxt-link>
            </form>
        </section>
    </main>
</template>
<script setup lang="ts">
const { auth } = useSupabaseClient();
const user = useSupabaseUser();

const userLogout = async () => {
    await auth.signOut();
};

watchEffect(() => {
    if (!user.value) {
        return navigateTo('/login');
    }
});

definePageMeta({
    middleware: 'auth',
});
</script>

<template>
    <main class="text-gray-400">
        <section v-if="user" class="mt-10 flex justify-center">
            <div class="text-center">
                <figure
                    class="inline-flex h-20 w-20 items-center justify-center rounded-full bg-gray-800 text-gray-600">
                    <img class="rounded-full" src="https://xsgames.co/randomusers/avatar.php?g=pixel" alt="" />
                </figure>
                <div class="flex flex-col items-center justify-center text-center">
                    <h1 class="tagline mt-4 text-5xl font-black">Welcome</h1>
                    <div class="mt-2 mb-4 h-1 w-12 rounded bg-[#42b883]"></div>

                    <h3 class="text-2xl font-bold text-[#aac8e4]">Email</h3>
                    <p class="text-base text-gray-400">{{ user.email }}</p>

                    <button @click="userLogout"
                        class="mt-8 rounded-md bg-[#42b883] px-4 py-2 font-sans font-bold text-[#213547] transition-colors duration-500 hover:bg-[#42d392] focus:outline-none">
                        logout
                    </button>
                </div>
            </div>
        </section>
    </main>
</template>
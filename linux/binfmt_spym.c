/*
 *  binfmt_spym.c 
 *
 *  Author: Mark Mossberg <mark.mossberg@gmail.com>
 */

#include <linux/module.h>
#include <linux/binfmts.h>
#include <linux/fs.h>

/*
 * Most of this is jacked from fs/binfmt_script.c
 */

MODULE_LICENSE("GPL");

#define SPYM_MAGIC "SPYM"
#define spym_info(fmt, ...) \
    pr_info("%s: " fmt, THIS_MODULE->name, ##__VA_ARGS__)

struct spym_header_t {
    char magic[4];
    unsigned int interp_off;
    unsigned int text_off;
    unsigned int text_size;
    unsigned int data_off;
    unsigned int data_size;
};

static int load_spym(struct linux_binprm *bprm)
{
    int retval;
    const char *interp;
    char interpbuf[BINPRM_BUF_SIZE];
    struct file *file;
    struct spym_header_t* hdr = (struct spym_header_t*) bprm->buf;

    /* Validate magic */
    if (memcmp(hdr->magic, SPYM_MAGIC, strlen(SPYM_MAGIC)))
        return -ENOEXEC;

    /* Parse out interpreter path */
    interp = bprm->buf + hdr->interp_off;

    /* Set up bprm to execute the interpreter with an argument of the
     * filename
     */

    /*
     * Ok, here's my understanding of how this works.
     *
     * bprm->p is basically a stack pointer to this process's internal kernel
     * stack. This stack is just like normal stacks in that they /grow down/
     * rather than up. This can be seen in the `copy_strings` function which
     * does `bprm->p -= len` where len is the length of a string it's
     * effectively pushing on the stack. This stack is also just like normal
     * stacks in that the arguments are pushed in reverse order such that
     * argv[0] is at the top of the stack (lowest in memory). This explains
     * the comment in fs/binfmt_script.c (line 60) which says it's splicing
     * in "reverse order, because of how the user environment and arguments
     * are stored."
     */

    /* Need to reset argv[0] from the thing executed to the interpreter.
     * This is basically a pop.
     */
    retval = remove_arg_zero(bprm);
    if (retval)
        return retval;

    /* Push our last argument; filename to execute. Currently it's stored
     * in bprm->interp. It was put there in do_execve_common().
     * copy_strings_kernel() is designed to accept (int) argc and (char**) argv
     * and push argv on the stack, so we hackily provide a 1 and a pointer
     * to bprm->interp to fake it.
     */
    retval = copy_strings_kernel(1, &bprm->interp, bprm);
    if (retval)
        return retval;

    /* Our responsibility to make sure bprm->argc is in a correct state,
     * and we just added an argument
     */
    bprm->argc++;

    /* Repeat the above for the interpreter path */
    retval = copy_strings_kernel(1, &interp, bprm);
    if (retval)
        return retval;
    bprm->argc++;

    /* Make sure we update bprm->interp */
    strcpy(interpbuf, interp);
    retval = bprm_change_interp(interpbuf, bprm);
    if (retval)
        return retval;

    /* Final preparations */
    file = open_exec(interp);
    if (IS_ERR(file))
        return PTR_ERR(file);

    bprm->file = file;
    retval = prepare_binprm(bprm);
    if (retval < 0)
        return retval;

    /* Restart process. We've literally changed the thing being executed,
     * so we need to start from the beginning of the execution process
     */
    spym_info("spym binary detected. executing...\n");
    return search_binary_handler(bprm);
}

static struct linux_binfmt spym_format = {
    .module = THIS_MODULE,
    .load_binary = load_spym,
};

static int __init init_spym_binfmt(void)
{
    spym_info("Registering spym format\n");
    register_binfmt(&spym_format);
    return 0;
}

static void exit_spym_binfmt(void)
{
    spym_info("Unregistering spym format\n");
    unregister_binfmt(&spym_format);
}

module_init(init_spym_binfmt);
module_exit(exit_spym_binfmt);

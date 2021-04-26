#ifndef OPOWPOOL_HEAVYHASH_H
#define OPOWPOOL_HEAVYHASH_H

#include <stdint.h>

void compute_blockheader_heavyhash(uint32_t* block_header, void* output);

#endif //OPOWPOOL_HEAVYHASH_H
"""CPU functionality."""

import sys, time

class CPU: # Main CPU class.

    def __init__(self): # Construct a new CPU.
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.ir = 0
        self.running = False
        self.trans_instructions = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b00000001: self.hlt,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
            0b01010010: self.inter,
            0b10000100: self.stor,
            0b01010100: self.jmp,
            0b01001000: self.pra,
            0b01010101: self.jeq,
            0b01010110: self.jne,
        }
        self.fl = 0b00000000 # 00000LGE
        self.intm = 5 # Interrupt Mask
        self.ints = 6 # Interrupt Status
        self.sp = 7 # Stack Pointer
        self.reg[self.sp] = 0xF4 # Decimal 243
        self.reg[self.ints] = 0b00000000 # Status
        self.reg[self.intm] = 0b00000000 # Mask

    def load(self):
        """Load a program into memory."""
        args = sys.argv

        address = 0
        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        if len(args) > 1:
            program = []
            with open(args[1]) as f:
                for line in f.readlines():
                    if "#" in line:
                        ind = line.index("#")
                        line = line[:ind]
                        line.strip()
                    if "\n" in line:
                        line = line.replace("\n", "")
                    if line != "" and line != "\n":
                        program.append(int(line,2))

        for instruction in program:
            self.ram[address] = instruction
            address += 1
        # print("instructions",self.ram)

    def alu(self): # ALU operations. Arithmetic Logic Unit
        reg_a = self.pc + 1
        reg_b = self.pc + 2

        def add():
            self.reg[self.ram[reg_a]] = self.reg[self.ram[reg_a]] + self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def sub():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] - self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def mul():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] * self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def div():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] / self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def mod():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] % self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def and_bw():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] & self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def or_bw():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] | self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def xor_bw():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] ^ self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def not_bw():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] - self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def shl_bw():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] << self.reg[self.ram[reg_b]]
            self.inc_pc()
        
        def shr_bw():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] >> self.reg[self.ram[reg_b]]
            self.inc_pc()

        def comp(): # 00000LGE
            reg_a_val = self.reg[self.ram[reg_a]]
            reg_b_val = self.reg[self.ram[reg_b]]
            if reg_a_val < reg_b_val:
                self.fl = 0b00000100
            elif reg_a_val > reg_b_val:
                self.fl = 0b00000010
            elif reg_a_val == reg_b_val:
                self.fl = 0b00000001
            else:
                print("Given values cannot be compared")
            self.inc_pc()

        instructions = {
            0b10100000: add,
            0b10100001: sub,
            0b10100010: mul,
            0b10100011: div,
            0b10100100: mod,
            0b10100111: comp,
            0b10101000: and_bw,
            0b10101010: or_bw,
            0b10101011: xor_bw,
            0b01101001: not_bw,
            0b10101100: shl_bw,
            0b10101101: shr_bw
        }

        try:
            func = instructions[self.ir]
            func()
        except:
            raise Exception("Unsupported ALU Operation")
    
    def cpu_instructions(self, inst, ram_a=None, ram_b=None):
        
        def ldi():
            self.reg[self.ram[ram_a]] = self.ram[ram_b]
        
        def prn():
            print(f"{self.reg[self.ram[ram_a]]}")
        
        def hlt():
            self.running = False

        cpu_inst = {
            "LDI": ldi,
            "PRN": prn,
            "HLT": hlt
        }

        try:
            func = cpu_inst[inst]
            func()
        except:
            raise Exception("Unsupported Instruction")
    
    def ram_read(self, pc):
        return self.ram[pc]
    
    def ram_write(self, pc, instruction):
        self.ram[pc] = instruction

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def inter(self):
        print('interrupt')
    
    def pra(self):
        print(chr(self.reg[self.ram[self.pc+1]]))
        self.inc_pc()
        
    
    def jmp(self):
        self.pc = self.reg[self.ram[self.pc+1]]

    def jeq(self):
        mask = 0b00000001
        eq_val = self.fl & mask
        if eq_val == 1:
            self.pc = self.reg[self.ram[self.pc+1]]
        else:
            self.inc_pc()
    
    def jne(self):
        mask = 0b00000001
        eq_val = self.fl & mask
        if eq_val != 1:
            self.pc = self.reg[self.ram[self.pc+1]]
        else:
            self.inc_pc()

    def stor(self):
        temp = self.reg[self.ram[self.pc+1]]
        self.reg[self.ram[self.pc+1]] = self.reg[self.ram[self.pc+2]]
        self.reg[self.ram[self.pc+1]] = temp
        self.inc_pc()

    def call(self):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + ((self.ir & 0b11000000) >> 6) + 1
        val = self.ram[self.pc+1]
        self.pc = self.reg[val]
    
    def ret(self):
        val = self.ram[self.reg[self.sp]]
        self.pc = val
        self.reg[self.sp] += 1

    def push(self):
        self.reg[self.sp] -= 1
        reg_num = self.ram[self.pc+1]
        reg_val = self.reg[reg_num]
        self.ram[self.reg[self.sp]] = reg_val
        self.inc_pc()
    
    def pop(self):
        val = self.ram[self.reg[self.sp]]
        reg_num = self.ram[self.pc+1]
        self.reg[reg_num] = val
        self.reg[self.sp] += 1
        self.inc_pc()

    def ldi(self):
        self.cpu_instructions("LDI", self.pc+1, self.pc+2)
        self.inc_pc()

    def prn(self):
        self.cpu_instructions("PRN", self.pc+1)
        self.inc_pc()

    def hlt(self):
        self.cpu_instructions("HLT")
        self.inc_pc()

    def inc_pc(self):
        self.pc += ((self.ir & 0b11000000) >> 6) + 1
    
    def int_timer_check(self):
        print("SET IS!")
        # self.intm = 5 # Interrupt Mask
        # self.ints = 6 # Interrupt Status
        mask = 0b00000001
        is_val = self.reg[self.ints]
        print('before',f'{self.reg[self.ints]:#010b}')
        self.reg[self.ints] = is_val | mask
        print('after',f'{self.reg[self.ints]:#010b}')
        time.sleep(2)

    def check_im(self):
        print("CHECK IM")
        int_im = self.reg[self.intm]
        time.sleep(0.01)
        if int_im > 0:
            print('int_im',int_im)
            print('after',f'{self.reg[self.ints]:#010b}')
            time.sleep(0.01)
            for i in range(8):
                print(f"for i: {i}")
                time.sleep(0.01)
                interrupt = ((int_im >> i) & self.reg[self.ints]) == 1
                print("interrupt", interrupt)
                if interrupt > 0:
                    print(f"{interrupt:#010b}")
                    mask = 0b00000000
                    
                    time.sleep(5)
        # self.intm = 5 # Interrupt Mask
        # self.ints = 6 # Interrupt Status


    def run(self):
        self.running = True
        count = 0
        # start_time = time.clock()
        # current_time = time.clock()

        while self.running:
            # current_time = time.clock()
            self.ir = self.ram_read(self.pc)
            # print(f"self.pc: {self.pc}")
            # print(f"self.ir: {self.ir:#010b}")
            # time_change = current_time-start_time
            # print("Time change:", time_change)
            # if time_change > 0.1:
            #     start_time = current_time
            #     self.int_timer_check()
            # self.check_im()
            alu_mask = 0b00100000
            is_alu = self.ir & alu_mask
            if is_alu > 0:
                # print(f"is_alu: {is_alu:#010b}")
                self.alu()
            else:
                try:
                    func = self.trans_instructions[self.ir]
                    func()
                except:
                    raise Exception("Unsupported Instruction")
                    sys.exit(1)


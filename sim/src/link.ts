// The radio: a serial link with a capacity. Telemetry (the newest range frame wins) is sent first; a photograph takes what is left,
// so while a photo transfers the map updates slow down. Delivery is delayed by a fixed latency.
import { LINK } from "./constants";
import { Packet } from "./firmware";

export interface PhotoXfer { total: number; sent: number; payload: unknown; rows: number }
export class Link {
  rate = LINK.rates[1];
  latency = LINK.latency;
  private queue: Packet[] = []; private head = 0;                // bytes already sent of queue[0]
  photo: PhotoXfer | null = null;
  private delivered: { at: number; pkt: Packet }[] = [];
  private photoDone: { at: number; payload: unknown }[] = [];
  utilization = 0;                                              // 0 to 1, smoothed
  bytesSent = 0;
  private carry = 0;

  send(p: Packet): void {
    if (p.kind === "tof") { const i = this.queue.findIndex((q, k) => q.kind === "tof" && !(k === 0 && this.head > 0)); if (i >= 0) this.queue.splice(i, 1); }   // newest frame wins
    this.queue.push(p);
  }
  startPhoto(totalBytes: number, rows: number, payload: unknown): void { this.photo = { total: totalBytes, sent: 0, payload, rows }; }
  get photoBusy(): boolean { return this.photo !== null; }
  get photoRows(): number { return this.photo ? Math.floor((this.photo.sent / this.photo.total) * this.photo.rows) : 0; }
  get photoProgress(): number { return this.photo ? this.photo.sent / this.photo.total : 0; }

  update(dt: number, t: number): void {
    const cap = (this.rate / 8) * (1 - LINK.overhead);          // bytes per second
    let budget = cap * dt + this.carry, used = 0;
    while (this.queue.length && budget >= 1) {
      const p = this.queue[0], left = p.bytes - this.head, take = Math.min(left, Math.floor(budget));
      if (take <= 0) break;
      this.head += take; budget -= take; used += take;
      if (this.head >= p.bytes) { this.queue.shift(); this.head = 0; this.delivered.push({ at: t + this.latency, pkt: p }); }
    }
    if (this.photo && budget >= 1) {
      const take = Math.min(this.photo.total - this.photo.sent, Math.floor(budget));
      this.photo.sent += take; budget -= take; used += take;
      if (this.photo.sent >= this.photo.total) { this.photoDone.push({ at: t + this.latency, payload: this.photo.payload }); this.photo = null; }
    }
    this.carry = Math.min(budget, 1);
    this.bytesSent += used;
    this.utilization += (Math.min(1, used / Math.max(cap * dt, 1e-9)) - this.utilization) * Math.min(1, dt / 1.0);
  }
  /** packets and finished photographs that have arrived at the console by time t */
  poll(t: number): { packets: Packet[]; photos: unknown[] } {
    const packets: Packet[] = [], photos: unknown[] = [];
    while (this.delivered.length && this.delivered[0].at <= t) packets.push(this.delivered.shift()!.pkt);
    while (this.photoDone.length && this.photoDone[0].at <= t) photos.push(this.photoDone.shift()!.payload);
    return { packets, photos };
  }
}
